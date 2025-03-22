#!/usr/bin/env python3
"""
Main entry point for Ambient Assistant.
"""

import os
import sys
import logging
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine

from dotenv import load_dotenv

from ambient.core.event_bus import EventBus, EventType
from ambient.core.settings_manager import SettingsManager
from ambient.core.app_manager import AppManager
from ambient.service.assistant_service import AssistantService
from ambient.ui.tray_icon import TrayIcon
from ambient.ui.response_window import ResponseWindow
from ambient.ui.settings_window import SettingsWindow


def setup_logging():
    """Setup logging configuration."""
    log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.expanduser('~/Library/Logs/AmbientAssistant/app.log'), 'a')
        ]
    )
    
    # Create log directory if it doesn't exist
    os.makedirs(os.path.expanduser('~/Library/Logs/AmbientAssistant'), exist_ok=True)
    
    logger = logging.getLogger('ambient')
    logger.setLevel(log_level)
    return logger


def main():
    """Main entry point for the application."""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Ambient Assistant")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Ambient Assistant")
    app.setApplicationDisplayName("Ambient Assistant")
    app.setOrganizationName("Ambient AI")
    app.setOrganizationDomain("ambient.ai")
    app.setQuitOnLastWindowClosed(False)
    
    # Create application components
    logger.info("Initializing core components")
    event_bus = EventBus()
    settings_manager = SettingsManager()
    app_manager = AppManager(event_bus, settings_manager)
    
    # Set application icon
    icon_path = str(Path(__file__).parent / "resources" / "icons" / "app_icon.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        logger.warning(f"Icon not found at {icon_path}")
    
    # Create UI components
    logger.info("Initializing UI components")
    tray_icon = TrayIcon(event_bus, settings_manager)
    response_window = ResponseWindow(event_bus, settings_manager)
    settings_window = SettingsWindow(event_bus, settings_manager)
    
    # Create service components
    logger.info("Initializing service components")
    assistant_service = AssistantService(event_bus, settings_manager)
    
    # Initialize and start components
    logger.info("Starting application")
    app_manager.initialize()
    tray_icon.initialize()
    assistant_service.start()
    
    # Connect Qt signals for clean shutdown
    app.aboutToQuit.connect(lambda: shutdown(assistant_service, app_manager, logger))
    
    # Emit application started event
    event_bus.publish(EventType.APP_STARTED, {})
    
    # Start event loop
    return app.exec()


def shutdown(assistant_service, app_manager, logger):
    """Perform clean shutdown of the application."""
    logger.info("Shutting down Ambient Assistant")
    assistant_service.stop()
    app_manager.shutdown()


if __name__ == "__main__":
    sys.exit(main())