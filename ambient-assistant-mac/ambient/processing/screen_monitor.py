import time
import os
from PIL import ImageGrab
import pytesseract
import logging
import re
from PyQt6.QtCore import QObject, pyqtSignal
from ambient.core.event_bus import Events

class ScreenMonitor(QObject):
    def __init__(self, event_bus, settings_manager):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        self.last_content = ""
        self.running = False
        
        # Set Tesseract path for macOS
        if os.path.exists('/usr/local/bin/tesseract'):
            pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        elif os.path.exists('/opt/homebrew/bin/tesseract'):
            pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
            
        # Subscribe to toggle events
        self.event_bus.subscribe(Events.TOGGLE_ACTIVE, self._handle_toggle)
        
    def _handle_toggle(self, active):
        """Handle monitor toggle."""
        if active and not self.running:
            # Start monitoring in a separate thread
            import threading
            self.running = True
            self.monitor_thread = threading.Thread(target=self.start_monitoring)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Screen monitoring started")
        else:
            # Stop monitoring
            self.running = False
            self.logger.info("Screen monitoring stopped")

    def start_monitoring(self):
        """Continuous screen monitoring."""
        self.logger.info("Starting continuous monitoring")
        
        while self.running:
            try:
                # Capture screen
                screenshot = ImageGrab.grab()
                current_content = pytesseract.image_to_string(screenshot)
                
                if self._content_changed(current_content):
                    self.logger.info("Significant content change detected")
                    
                    # Send to event bus
                    self.event_bus.publish(Events.QUESTION_DETECTED, 
                                         f"I noticed your screen content changed. Here's what I see:\n\n{current_content}\n\nLet me analyze this for you.")
                    
                    # Update last content
                    self.last_content = current_content
                
                # Wait for next capture
                interval = self.settings_manager.get_setting("SCREEN_CAPTURE_INTERVAL", 2)
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring: {e}")
                time.sleep(1)
                
    def _content_changed(self, new_content):
        """Detect significant content changes."""
        if not new_content.strip() or not self.last_content.strip():
            return False
            
        # Simple diff check
        words1 = set(self.last_content.split())
        words2 = set(new_content.split())
        
        # Check for significant difference
        if len(words1) == 0:
            return len(words2) > 5
        
        difference = len(words1.symmetric_difference(words2))
        return difference / len(words1) > 0.3  # 30% change threshold