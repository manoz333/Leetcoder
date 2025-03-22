"""UI component builder for creating and configuring UI elements."""
from PyQt6.QtWidgets import (
    QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget,
    QSizeGrip, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from ambient.ui.components.styles import Styles


class UIBuilder:
    """Utility class for creating UI components with proper styling."""
    
    @staticmethod
    def create_title_bar(parent, title_text="Ambient Teacher Assistant"):
        """Create the title bar with drag handling."""
        title_bar = QWidget()
        title_bar.setCursor(Qt.CursorShape.SizeAllCursor)
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("background-color: transparent;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 5, 5, 5)
        
        # Title label
        title_label = QLabel(f"🤖 {title_text}")
        title_label.setStyleSheet(Styles.TITLE_LABEL)
        title_layout.addWidget(title_label)
        
        # Status indicator
        status_label = QLabel("Ready")
        status_label.setStyleSheet(Styles.STATUS_LABEL)
        title_layout.addWidget(status_label)
        
        # Demo mode indicator
        demo_label = QLabel("DEMO MODE")
        demo_label.setStyleSheet(Styles.DEMO_LABEL)
        demo_label.hide()
        title_layout.addWidget(demo_label)
        
        # Mode indicator
        mode_label = QLabel("Mode: Normal")
        mode_label.setStyleSheet(Styles.MODE_LABEL)
        title_layout.addWidget(mode_label)
        
        title_layout.addStretch()
        
        # Close button
        close_button = QPushButton("✕")
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet(Styles.CLOSE_BUTTON)
        title_layout.addWidget(close_button)
        
        return title_bar, title_label, status_label, demo_label, mode_label, close_button
    
    @staticmethod
    def create_mode_buttons():
        """Create mode selection buttons."""
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(0, 0, 0, 10)
        
        mode_group = QButtonGroup()
        mode_group.setExclusive(True)
        
        # Explainer mode button (formerly Suggester)
        suggester_btn = QPushButton("👨‍🏫 Explainer (Step-by-Step)")
        suggester_btn.setCheckable(True)
        suggester_btn.setChecked(True)  # Default to Explainer mode
        suggester_btn.setStyleSheet(Styles.MODE_BUTTON)
        mode_group.addButton(suggester_btn)
        mode_layout.addWidget(suggester_btn)
        
        # Code Solver mode button
        solver_btn = QPushButton("🧩 Code Solver (Complete Solution)")
        solver_btn.setCheckable(True)
        solver_btn.setStyleSheet(Styles.MODE_BUTTON)
        mode_group.addButton(solver_btn)
        mode_layout.addWidget(solver_btn)
        
        # Return null for normal_btn since it's removed
        normal_btn = None
        
        return mode_layout, mode_group, normal_btn, suggester_btn, solver_btn
    
    @staticmethod
    def create_response_area():
        """Create the response text area."""
        response_text = QTextEdit()
        response_text.setReadOnly(True)
        response_text.setFont(QFont("Menlo", 13))
        response_text.setStyleSheet(Styles.RESPONSE_TEXT)
        response_text.setAcceptRichText(True)
        
        return response_text
    
    @staticmethod
    def create_question_input():
        """Create the question input area."""
        question_input = QTextEdit()
        question_input.setPlaceholderText("Ask a coding question...")
        question_input.setFixedHeight(60)
        question_input.setFont(QFont("Menlo", 12))
        question_input.setStyleSheet(Styles.QUESTION_INPUT)
        
        return question_input
    
    @staticmethod
    def create_control_buttons():
        """Create control buttons for actions."""
        button_layout = QHBoxLayout()
        
        # Ask button
        ask_button = QPushButton("💬 Ask (⌘+Enter)")
        ask_button.setStyleSheet(Styles.CONTROL_BUTTON)
        button_layout.addWidget(ask_button)
        
        # Screenshot button
        screenshot_button = QPushButton("📷 Screenshot (⌘+S)")
        screenshot_button.setStyleSheet(Styles.CONTROL_BUTTON)
        button_layout.addWidget(screenshot_button)
        
        # Voice button
        voice_button = QPushButton("🎤 Voice (⌘+V)")
        voice_button.setStyleSheet(Styles.CONTROL_BUTTON)
        button_layout.addWidget(voice_button)
        
        # Monitor toggle button
        monitor_button = QPushButton("👁️ Start Monitoring")
        monitor_button.setStyleSheet(Styles.CONTROL_BUTTON)
        button_layout.addWidget(monitor_button)
        
        # Clear button
        clear_button = QPushButton("🗑️ Clear")
        clear_button.setStyleSheet(Styles.CONTROL_BUTTON)
        button_layout.addWidget(clear_button)
        
        return button_layout, ask_button, screenshot_button, voice_button, monitor_button, clear_button
    
    @staticmethod
    def create_size_grip(parent):
        """Create a size grip for window resizing."""
        size_grip = QSizeGrip(parent)
        size_grip.setStyleSheet("background: transparent;")
        grip_layout = QHBoxLayout()
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addStretch()
        grip_layout.addWidget(size_grip)
        
        return grip_layout
    
    @staticmethod
    def setup_shortcuts(parent, callbacks):
        """Set up keyboard shortcuts."""
        shortcuts = {}
        
        # Ask shortcut (Cmd+Enter)
        shortcuts['ask'] = QShortcut(QKeySequence("Ctrl+Return"), parent)
        shortcuts['ask'].activated.connect(callbacks.get('ask', lambda: None))
        
        # Screenshot shortcut (Cmd+S)
        shortcuts['screenshot'] = QShortcut(QKeySequence("Ctrl+S"), parent)
        shortcuts['screenshot'].activated.connect(callbacks.get('screenshot', lambda: None))
        
        # Voice shortcut (Cmd+V)
        shortcuts['voice'] = QShortcut(QKeySequence("Ctrl+V"), parent)
        shortcuts['voice'].activated.connect(callbacks.get('voice', lambda: None))
        
        # Monitor shortcut (Cmd+M)
        shortcuts['monitor'] = QShortcut(QKeySequence("Ctrl+M"), parent)
        shortcuts['monitor'].activated.connect(callbacks.get('monitor', lambda: None))
        
        # Mode shortcuts
        shortcuts['normal'] = QShortcut(QKeySequence("Ctrl+1"), parent)
        shortcuts['normal'].activated.connect(callbacks.get('normal_mode', lambda: None))
        
        shortcuts['suggester'] = QShortcut(QKeySequence("Ctrl+2"), parent)
        shortcuts['suggester'].activated.connect(callbacks.get('suggester_mode', lambda: None))
        
        shortcuts['solver'] = QShortcut(QKeySequence("Ctrl+3"), parent)
        shortcuts['solver'].activated.connect(callbacks.get('solver_mode', lambda: None))
        
        return shortcuts 