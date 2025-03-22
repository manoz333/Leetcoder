"""UI styles for the application."""


class Styles:
    """Styles for UI components."""
    
    # Main window and container styles
    CONTENT_WIDGET = """
        QWidget {
            background-color: rgba(60, 60, 65, 60);
            border-radius: 15px;
            border: 1px solid rgba(220, 220, 220, 70);
        }
    """
    
    # Text styles
    TITLE_LABEL = """
        QLabel {
            color: #FFFFFF;
            font-size: 16px;
            font-weight: bold;
            background-color: rgba(60, 60, 70, 80);
            padding: 3px 8px;
            border-radius: 8px;
        }
    """
    
    STATUS_LABEL = """
        QLabel {
            color: #00FF00;
            font-size: 12px;
            font-weight: bold;
            padding: 4px;
            background-color: rgba(60, 60, 70, 80);
            border-radius: 4px;
        }
    """
    
    DEMO_LABEL = """
        QLabel {
            color: #FFCC00;
            font-weight: bold;
            padding: 2px 8px;
            background-color: rgba(60, 60, 70, 80);
            border-radius: 4px;
        }
    """
    
    MODE_LABEL = """
        QLabel {
            color: #FFFFFF;
            font-size: 12px;
            padding: 4px;
            background-color: rgba(60, 60, 70, 80);
            border-radius: 4px;
        }
    """
    
    MODE_LABEL_SUGGESTER = """
        QLabel {
            color: #AAFFAA;
            font-size: 12px;
            padding: 4px;
            background-color: rgba(50, 90, 50, 90);
            border-radius: 4px;
        }
    """
    
    MODE_LABEL_SOLVER = """
        QLabel {
            color: #AAAAFF;
            font-size: 12px;
            padding: 4px;
            background-color: rgba(50, 50, 100, 90);
            border-radius: 4px;
        }
    """
    
    # Button styles
    CLOSE_BUTTON = """
        QPushButton {
            background-color: rgba(120, 120, 120, 60);
            color: #FFFFFF;
            font-size: 16px;
            border: none;
            border-radius: 15px;
        }
        QPushButton:hover {
            background-color: rgba(220, 70, 70, 120);
            color: white;
        }
    """
    
    MODE_BUTTON = """
        QPushButton {
            background-color: rgba(90, 90, 95, 80);
            color: white;
            border: 1px solid rgba(200, 200, 200, 60);
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: rgba(110, 110, 115, 100);
        }
        QPushButton:pressed {
            background-color: rgba(70, 70, 75, 110);
        }
        QPushButton:checked {
            background-color: rgba(90, 110, 150, 100);
            border: 1px solid rgba(120, 170, 255, 100);
            font-weight: bold;
        }
    """
    
    CONTROL_BUTTON = """
        QPushButton {
            background-color: rgba(90, 90, 95, 100);
            color: white;
            border: 1px solid rgba(170, 170, 170, 60);
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: rgba(110, 110, 115, 120);
        }
        QPushButton:pressed {
            background-color: rgba(70, 70, 75, 120);
        }
        QPushButton:disabled {
            background-color: rgba(70, 70, 75, 60);
            color: rgba(170, 170, 170, 170);
        }
    """
    
    # Text areas
    RESPONSE_TEXT = """
        QTextEdit {
            background-color: rgba(50, 50, 55, 50);
            color: #FFFFFF;
            border: 1px solid rgba(170, 170, 170, 80);
            border-radius: 10px;
            padding: 10px;
            selection-background-color: rgba(120, 170, 255, 120);
        }
        QScrollBar:vertical {
            background-color: rgba(50, 50, 55, 40);
            width: 14px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: rgba(170, 170, 170, 80);
            min-height: 20px;
            border-radius: 7px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """
    
    QUESTION_INPUT = """
        QTextEdit {
            background-color: rgba(70, 70, 75, 80);
            color: #FFFFFF;
            border: 1px solid rgba(170, 170, 170, 80);
            border-radius: 8px;
            padding: 8px;
        }
        QTextEdit::placeholder {
            color: rgba(200, 200, 200, 150);
        }
    """ 