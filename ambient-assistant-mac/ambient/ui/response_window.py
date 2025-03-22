"""Main response window UI for Ambient Assistant."""
import logging
import time
import threading
import tempfile
import re
import uuid
from PyQt6.QtWidgets import (QMainWindow, QTextEdit, QVBoxLayout, QWidget, 
                             QPushButton, QHBoxLayout, QLabel, QSizeGrip, QApplication,
                             QButtonGroup)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSlot, QThread, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QShortcut, QKeySequence, QTextCursor, QColor, QTextCharFormat, QPalette
from ambient.core.event_bus import Events
from ambient.core.enums import AssistantMode
from ambient.ui.components import UIBuilder, ResponseHandler
from ambient.ui.workers import ScreenshotWorker, VoiceWorker, ScreenMonitorWorker

# New enum for Assistant modes
class AssistantMode:
    NORMAL = "normal"
    SUGGESTER = "suggester"
    SOLVER = "solver"

# Add syntax highlighting colors (used for HTML formatting)
class CodeColors:
    KEYWORD = "#569CD6"     # Blue
    STRING = "#CE9178"      # Orange
    COMMENT = "#6A9955"     # Green
    FUNCTION = "#DCDCAA"    # Yellow
    CLASS = "#4EC9B0"       # Teal
    NUMBER = "#B5CEA8"      # Light Green
    OPERATOR = "#D4D4D4"    # Light Gray
    VARIABLE = "#9CDCFE"    # Light Blue
    BACKGROUND = "#1E1E1E"  # Dark Gray
    TEXT = "#D4D4D4"        # Light Gray

class ScreenshotWorker(QThread):
    """Worker thread for screenshot capture to avoid UI freezes."""
    finished = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            from PIL import ImageGrab
            import pytesseract
                
            # Capture screen
            screenshot = ImageGrab.grab()
            content = pytesseract.image_to_string(screenshot)
            
            if content.strip():
                self.finished.emit(content)
            else:
                self.status.emit("No text detected in screenshot")
                
        except Exception as e:
            self.error.emit(str(e))

class VoiceWorker(QThread):
    """Worker thread for voice input using OpenAI Whisper API."""
    finished = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.logger = logging.getLogger(__name__)

    def run(self):
        try:
            from openai import OpenAI
            import sounddevice as sd
            import soundfile as sf
            import numpy as np
            
            self.status.emit("Listening... Speak now")
            
            # Record audio
            fs = 44100  # Sample rate
            duration = 5  # seconds
            self.status.emit(f"Recording for {duration} seconds...")
            
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished
            
            # Save to temporary file
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            sf.write(temp_audio.name, recording, fs)
            
            # Get API key
            api_key = self.settings_manager.get_setting('openai_api_key')
            if not api_key:
                raise ValueError("OpenAI API key not found in settings")
                
            # Use OpenAI Whisper API
            client = OpenAI(api_key=api_key)
            self.status.emit("Processing speech with Whisper API...")
            
            with open(temp_audio.name, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    prompt="This is a coding assistant. The user may ask about programming languages, code, or technical concepts."
                )
            
            # Clean up temp file
            import os
            os.unlink(temp_audio.name)
            
            if transcription.text:
                self.finished.emit(transcription.text)
            else:
                self.status.emit("No speech detected")
                
        except ImportError as e:
            self.error.emit(f"Required packages not installed: {str(e)}")
            self.logger.error(f"Import error in voice processing: {str(e)}")
        except Exception as e:
            self.error.emit(str(e))
            self.logger.error(f"Error in voice processing: {str(e)}")

class ScreenMonitorWorker(QThread):
    """Worker thread for continuous screen monitoring."""
    content_detected = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.active = False
        self.logger = logging.getLogger(__name__)
        
    def set_active(self, active):
        self.active = active
        if not active and self.isRunning():
            self.terminate()
    
    def run(self):
        try:
            from PIL import ImageGrab
            import pytesseract
            import pyautogui
            
            self.status.emit("Starting continuous monitoring...")
            
            while self.active:
                # Get mouse position
                x, y = pyautogui.position()
                
                # Capture screen area around mouse (500x500 pixels)
                x1 = max(0, x - 250)
                y1 = max(0, y - 250)
                x2 = x + 250
                y2 = y + 250
                
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                content = pytesseract.image_to_string(screenshot)
                
                if content.strip():
                    self.content_detected.emit(content)
                    self.status.emit("Content detected near cursor")
                
                # Wait 5 seconds before next capture
                for _ in range(50):  # Check every 100ms if still active
                    if not self.active:
                        break
                    time.sleep(0.1)
                    
        except Exception as e:
            self.error.emit(str(e))
            self.logger.error(f"Error in screen monitoring: {str(e)}")

class ResponseWindow(QMainWindow):
    """Main UI window for the Ambient Assistant application."""
    
    def __init__(self, event_bus, settings_manager):
        """Initialize response window UI and handlers."""
        super().__init__(None)
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        self.monitoring_active = False
        self.drag_pos = None
        self.assistant_mode = AssistantMode.NORMAL
        
        # Track active response stream
        self.current_response_id = None
        self.last_question_position = None
        
        # Initialize UI
        self._init_ui()
        
        # Install event filter to prevent window hiding
        self.installEventFilter(self)
        
        # Initialize workers
        self.screenshot_worker = None
        self.voice_worker = None
        self.screen_monitor = ScreenMonitorWorker()
        self.screen_monitor.content_detected.connect(self._handle_monitored_content)
        self.screen_monitor.status.connect(self._update_status)
        self.screen_monitor.error.connect(self._handle_monitor_error)
        
        # Connect event handlers
        self.event_bus.subscribe(Events.RESPONSE_READY, self._handle_response)
        self.event_bus.subscribe(Events.RESPONSE_CHUNK, self._handle_response_chunk)
        
        # Show the window
        self.response_handler.set_welcome_message()
        self.show()
        
    def _init_ui(self):
        """Initialize the modern UI components."""
        # Set window properties
        self.setWindowTitle("Ambient Teacher Assistant")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)  # macOS specific to prevent hiding
        
        # Also set the window to be active
        QTimer.singleShot(100, self.activateWindow)
        
        # Main container
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content widget with transparent background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(50, 50, 55, 40);
                border-radius: 15px;
                border: 1px solid rgba(200, 200, 200, 50);
            }
        """)
        main_layout.addWidget(content_widget)
        
        # Content layout
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Create title bar
        title_bar, title_label, self.status_label, self.demo_label, self.mode_label, close_button = UIBuilder.create_title_bar(self)
        close_button.clicked.connect(self._quit_application)
        layout.addWidget(title_bar)
        
        # Create response area
        self.response_text = UIBuilder.create_response_area()
        layout.addWidget(self.response_text)
        
        # Initialize response handler - MOVED UP before setting modes
        self.response_handler = ResponseHandler(self.response_text, self.status_label)
        
        # Create mode selection buttons
        mode_layout, self.mode_group, self.normal_btn, self.suggester_btn, self.solver_btn = UIBuilder.create_mode_buttons()
        if self.normal_btn:
            self.normal_btn.clicked.connect(lambda: self._set_assistant_mode(AssistantMode.NORMAL))
        self.suggester_btn.clicked.connect(lambda: self._set_assistant_mode(AssistantMode.SUGGESTER))
        self.solver_btn.clicked.connect(lambda: self._set_assistant_mode(AssistantMode.SOLVER))
        layout.addLayout(mode_layout)
        
        # Set default mode to SUGGESTER since NORMAL is removed
        self._set_assistant_mode(AssistantMode.SUGGESTER)
        
        # Create question input
        self.question_input = UIBuilder.create_question_input()
        layout.addWidget(self.question_input)
        
        # Create control buttons
        button_layout, self.ask_button, self.screenshot_button, self.voice_button, self.monitor_button, self.clear_button = UIBuilder.create_control_buttons()
        self.ask_button.clicked.connect(self._handle_question)
        self.screenshot_button.clicked.connect(self._take_screenshot)
        self.voice_button.clicked.connect(self._start_voice_input)
        self.monitor_button.clicked.connect(self._toggle_monitoring)
        self.clear_button.clicked.connect(self.response_text.clear)
        layout.addLayout(button_layout)
        
        # Create size grip
        grip_layout = UIBuilder.create_size_grip(self)
        layout.addLayout(grip_layout)
        
        # Set up shortcuts
        self.shortcuts = UIBuilder.setup_shortcuts(self, {
            'ask': self._handle_question,
            'screenshot': self._take_screenshot,
            'voice': self._start_voice_input,
            'monitor': self._toggle_monitoring,
            'normal_mode': lambda: self._set_assistant_mode(AssistantMode.NORMAL),
            'suggester_mode': lambda: self._set_assistant_mode(AssistantMode.SUGGESTER),
            'solver_mode': lambda: self._set_assistant_mode(AssistantMode.SOLVER)
        })
        
        # Remove redundant initialization
        # self.response_handler = ResponseHandler(self.response_text, self.status_label)
        
        # Set window size
        self.resize(800, 600)
        self._center_window()
        
    def _center_window(self):
        """Center window on screen."""
        screen = self.screen().geometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)
        
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if hasattr(self, 'drag_pos') and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
    
    def _set_assistant_mode(self, mode):
        """Change the assistant mode and update UI."""
        self.assistant_mode = mode
        
        if mode == AssistantMode.NORMAL:
            self.mode_label.setText("Mode: Normal")
            self.mode_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 12px;
                    padding: 4px;
                    background-color: rgba(60, 60, 65, 80);
                    border-radius: 4px;
                }
            """)
            self._update_status("Normal mode active")
            
        elif mode == AssistantMode.SUGGESTER:
            self.mode_label.setText("Mode: Suggester")
            self.mode_label.setStyleSheet("""
                QLabel {
                    color: #AAFFAA;
                    font-size: 12px;
                    padding: 4px;
                    background-color: rgba(40, 80, 40, 80);
                    border-radius: 4px;
                }
            """)
            self._update_status("Suggester mode active - providing step-by-step guidance")
            
        elif mode == AssistantMode.SOLVER:
            self.mode_label.setText("Mode: Solver")
            self.mode_label.setStyleSheet("""
                QLabel {
                    color: #AAAAFF;
                    font-size: 12px;
                    padding: 4px;
                    background-color: rgba(40, 40, 80, 80);
                    border-radius: 4px;
                }
            """)
            self._update_status("Solver mode active - providing complete solutions")
            
        # Tell event bus about mode change
        self.event_bus.publish(Events.SETTINGS_CHANGED, {'assistant_mode': mode})
        
    def _handle_question(self):
        """Handle question input."""
        question = self.question_input.toPlainText().strip()
        if not question:
            return
            
        # Format the question and get response ID
        response_id = self.response_handler.format_question(question, self.assistant_mode)
        
        # Clear the input
        self.question_input.clear()
        
        # Send to LLM with mode information and response ID
        self.event_bus.publish(Events.QUESTION_DETECTED, {
            'text': question,
            'mode': self.assistant_mode,
            'response_id': response_id
        })

    @pyqtSlot()
    def _take_screenshot(self):
        """Take a manual screenshot with proper thread handling."""
        if self.screenshot_worker is not None and self.screenshot_worker.isRunning():
            return
            
        self.screenshot_worker = ScreenshotWorker()
        self.screenshot_worker.finished.connect(self._handle_screenshot_result)
        self.screenshot_worker.status.connect(self._update_status)
        self.screenshot_worker.error.connect(self._handle_screenshot_error)
        
        self.screenshot_button.setEnabled(False)
        self._update_status("Taking screenshot...")
        self.screenshot_worker.start()

    @pyqtSlot(str)
    def _handle_screenshot_result(self, content):
        """Handle screenshot result safely on main thread."""
        self.screenshot_button.setEnabled(True)
        
        if content:
            # Format the screenshot content and get response ID and prompt
            response_id, prompt_text = self.response_handler.format_screenshot_content(content, self.assistant_mode)
            
            self._update_status("Analyzing screenshot...")
                
            # Send to LLM with mode information and response ID
            self.event_bus.publish(Events.QUESTION_DETECTED, {
                'text': prompt_text,
                'mode': self.assistant_mode,
                'response_id': response_id
            })
        else:
            self._update_status("No text detected")

    @pyqtSlot(str)
    def _handle_screenshot_error(self, error_msg):
        """Handle screenshot errors safely."""
        self.screenshot_button.setEnabled(True)
        self._update_status(f"Screenshot error: {error_msg}")
        self.response_handler._append_response(f"### Screenshot Error\n\n{error_msg}\n\nPlease make sure you have the required packages installed:\n```\npip install Pillow pytesseract\n```\n\nFor Mac, you may also need to install Tesseract:\n```\nbrew install tesseract\n```")

    @pyqtSlot()
    def _start_voice_input(self):
        """Start voice input using OpenAI Whisper API."""
        if self.voice_worker is not None and self.voice_worker.isRunning():
            return
            
        self.voice_worker = VoiceWorker(self.settings_manager)
        self.voice_worker.finished.connect(self._handle_voice_result)
        self.voice_worker.status.connect(self._update_status)
        self.voice_worker.error.connect(self._handle_voice_error)
        
        self.voice_button.setEnabled(False)
        self._update_status("Initializing voice...")
        self.voice_worker.start()

    @pyqtSlot(str)
    def _handle_voice_result(self, text):
        """Handle transcribed voice input."""
        self.voice_button.setEnabled(True)
        if text:
            # Format the voice input and get response ID
            response_id = self.response_handler.format_voice_input(text, self.assistant_mode)
            
            # Send to LLM with mode information and response ID
            self.event_bus.publish(Events.QUESTION_DETECTED, {
                'text': text,
                'mode': self.assistant_mode,
                'response_id': response_id
            })

    @pyqtSlot(str)
    def _handle_voice_error(self, error_msg):
        """Handle voice processing errors."""
        self.voice_button.setEnabled(True)
        self._update_status(f"Voice error: {error_msg}")
        self.response_handler._append_response(f"""### Voice Input Error

{error_msg}

Please make sure you have the required packages installed:
```
pip install openai sounddevice soundfile numpy
```

For Mac, you may also need:
```
brew install portaudio
```

Then try again.""")

    @pyqtSlot(str)
    def _handle_monitored_content(self, content):
        """Handle content from continuous monitoring."""
        # Format the content based on the monitoring content
        response_id, prompt_text = self.response_handler.format_screenshot_content(content, self.assistant_mode)
        
        # Modify prompt to include context about continuous monitoring
        if self.assistant_mode == AssistantMode.SUGGESTER:
            prompt_text = f"Acting as a coding teacher, analyze this code without providing complete solutions. This content was captured near the user's cursor during continuous monitoring. Give hints, explain concepts, and suggest improvements:\n\n{content}"
        elif self.assistant_mode == AssistantMode.SOLVER:
            prompt_text = f"This content was captured near the user's cursor during continuous monitoring. Provide a detailed step-by-step solution. Include explanations for each step, proper comments, and the complete solution:\n\n{content}"
        else:
            prompt_text = f"This content was captured near the user's cursor during continuous monitoring. Provide helpful suggestions or information about this code or text:\n\n{content}"
            
        # Send to LLM with mode information and response ID
        self.event_bus.publish(Events.QUESTION_DETECTED, {
            'text': prompt_text,
            'mode': self.assistant_mode,
            'response_id': response_id
        })

    @pyqtSlot(str)
    def _handle_monitor_error(self, error_msg):
        """Handle monitoring errors."""
        self._update_status(f"Monitoring error: {error_msg}")
        self.monitoring_active = False
        self.monitor_button.setText("👁️ Start Monitoring")
        
    def _toggle_monitoring(self):
        """Toggle continuous monitoring."""
        self.monitoring_active = not self.monitoring_active
        
        if self.monitoring_active:
            self.monitor_button.setText("👁️ Stop Monitoring")
            self._update_status("Continuous monitoring active")
            self.screen_monitor.set_active(True)
            self.screen_monitor.start()
            self.event_bus.publish(Events.TOGGLE_ACTIVE, True)
        else:
            self.monitor_button.setText("👁️ Start Monitoring")
            self._update_status("Monitoring stopped")
            self.screen_monitor.set_active(False)
            self.event_bus.publish(Events.TOGGLE_ACTIVE, False)
    
    @pyqtSlot(object)
    def _handle_response(self, response_data):
        """Handle LLM response."""
        print(f"DEBUG: _handle_response called with data: {response_data}")
        self.logger.info(f"Response received: {type(response_data)}")
        self.response_handler.handle_response(response_data)
    
    @pyqtSlot(dict)
    def _handle_response_chunk(self, chunk_data):
        """Handle streaming response chunks."""
        print(f"DEBUG: _handle_response_chunk called with data: {chunk_data}")
        self.logger.info(f"Response chunk received: {len(chunk_data.get('text', ''))} chars")
        self.response_handler.handle_response_chunk(chunk_data)
    
    def _update_status(self, message):
        """Update status message."""
        self.response_handler._update_status(message)
        
    def update_demo_mode(self, is_demo):
        """Update UI for demo mode."""
        self.demo_label.setVisible(is_demo)
        if is_demo:
            self._update_status("Running in demo mode - API key not set")
    
    def _quit_application(self):
        """Properly quit the application."""
        self.event_bus.publish(Events.SHUTDOWN)

    def eventFilter(self, obj, event):
        """Handle events to prevent window from hiding when focus changes."""
        if event.type() == QEvent.Type.WindowDeactivate:
            # When window loses focus, ensure it stays visible
            QTimer.singleShot(100, self.show)
            QTimer.singleShot(200, self.activateWindow)
        return super().eventFilter(obj, event) 