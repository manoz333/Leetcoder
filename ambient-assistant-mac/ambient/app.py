import logging
import sys
import os
import signal
import importlib.util
import subprocess

from ambient.utils.logging_utils import setup_logging
from ambient.core.event_bus import EventBus, Events
from ambient.core.settings_manager import SettingsManager
from ambient.llm.model_manager import ModelManager
from ambient.ui.response_window import ResponseWindow
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

class AmbientAssistant:
    """Main application class for Ambient Assistant."""
    
    def __init__(self):
        # Initialize logging
        self.logger = setup_logging()
        self.logger.info("Starting Ambient Assistant")
        
        # Check for required dependencies
        self._check_dependencies()
        
        # Initialize core components
        self.event_bus = EventBus()
        self.settings_manager = SettingsManager()
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("Ambient Assistant")
        
        # Initialize LLM
        self.model_manager = ModelManager(self.event_bus, self.settings_manager)
        
        # Initialize UI
        self.response_window = ResponseWindow(self.event_bus, self.settings_manager)
        
        # Set up system tray
        self._setup_tray()
        
        # Connect event handlers
        self.event_bus.subscribe(Events.QUESTION_DETECTED, self._handle_question)
        self.event_bus.subscribe(Events.SHUTDOWN, self._handle_shutdown)
        self.event_bus.subscribe(Events.SETTINGS_CHANGED, self._handle_settings_changed)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        # Update UI with demo mode
        self.response_window.update_demo_mode(self.model_manager.demo_mode)
        
        self.logger.info("Ambient Assistant initialized")
    
    def _check_dependencies(self):
        """Check for required dependencies and prompt to install if missing."""
        required_packages = {
            'openai': 'openai',
            'PyQt6': 'PyQt6',
            'pillow': 'PIL',
            'sounddevice': 'sounddevice',
            'soundfile': 'soundfile',
            'pytesseract': 'pytesseract',
            'pyautogui': 'pyautogui',
            'python-dotenv': 'dotenv',
            'langchain-community': 'langchain_community'
        }
        
        missing_packages = []
        
        for package, import_name in required_packages.items():
            if not importlib.util.find_spec(import_name):
                missing_packages.append(package)
        
        if missing_packages:
            self.logger.warning(f"Missing dependencies: {', '.join(missing_packages)}")
            
            # Try to install missing packages
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + missing_packages)
                self.logger.info(f"Successfully installed missing dependencies: {', '.join(missing_packages)}")
            except Exception as e:
                self.logger.error(f"Failed to install missing dependencies: {e}")
                # We'll continue anyway, as the UI will handle missing dependencies gracefully
    
    def _setup_tray(self):
        """Set up system tray icon and menu."""
        # Find icon file
        icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app_icon.png")
        if not os.path.exists(icon_path):
            self.logger.warning(f"Icon not found at {icon_path}, using fallback")
            # Use system icon as fallback
            self.tray_icon = QSystemTrayIcon(self.app)
        else:
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self.app)
        
        # Create menu
        menu = QMenu()
        
        # Add actions
        show_action = menu.addAction("Show Assistant")
        show_action.triggered.connect(self._show_assistant)
        
        toggle_action = menu.addAction("Start Monitoring")
        toggle_action.triggered.connect(self._toggle_monitoring)
        self.toggle_action = toggle_action
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self._quit)
        
        # Set menu and show tray icon
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("Ambient Assistant")
        self.tray_icon.show()
        
        # Connect signals
        self.tray_icon.activated.connect(self._tray_activated)
    
    def _show_assistant(self):
        """Show the response window."""
        self.response_window.show()
        self.response_window.raise_()
        self.response_window.activateWindow()
    
    def _toggle_monitoring(self):
        """Toggle monitoring state."""
        is_active = not self.toggle_action.text().startswith("Start")
        
        if is_active:
            self.toggle_action.setText("Start Monitoring")
        else:
            self.toggle_action.setText("Stop Monitoring")
            
        self.event_bus.publish(Events.TOGGLE_ACTIVE, not is_active)
    
    def _tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - toggle visibility
            if self.response_window.isVisible():
                self.response_window.hide()
            else:
                self._show_assistant()
    
    def _handle_question(self, question):
        """Handle detected questions."""
        # Get the question text and mode
        if isinstance(question, dict):
            question_text = question.get('text', '')
            mode = question.get('mode', 'normal')
            self.logger.info(f"Processing question in {mode} mode: {question_text[:50]}...")
        else:
            # For backward compatibility
            question_text = question
            mode = 'normal'
            self.logger.info(f"Processing question: {question_text[:50]}...")
        
        # Generate response - pass the entire question object to maintain the mode info
        response = self.model_manager.generate_response(question)
        
        # Publish response
        self.event_bus.publish(Events.RESPONSE_READY, response)
    
    def _handle_settings_changed(self, settings):
        """Handle settings changes."""
        self.logger.info("Settings changed")
        
        # Update UI with demo mode
        if 'demo_mode' in settings:
            self.response_window.update_demo_mode(settings['demo_mode'])
    
    def _handle_shutdown(self):
        """Handle application shutdown."""
        self.logger.info("Shutting down")
        self.app.quit()
    
    def _handle_signal(self, signum, frame):
        """Handle system signals."""
        self.logger.info(f"Received signal {signum}")
        self._quit()
    
    def _quit(self):
        """Quit the application."""
        self.logger.info("Quitting application")
        self.event_bus.publish(Events.SHUTDOWN)
        self.app.quit()
    
    def run(self):
        """Run the application."""
        self.logger.info("Starting event loop")
        # Show window on startup
        self._show_assistant()
        return self.app.exec()

def main():
    """Main entry point."""
    assistant = AmbientAssistant()
    return assistant.run()

if __name__ == "__main__":
    sys.exit(main()) 