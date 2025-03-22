"""Worker thread for continuous screen monitoring."""
import logging
import time
import os
import sys
import tempfile
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal


class ScreenMonitorWorker(QThread):
    """Worker thread for continuous screen monitoring."""
    content_detected = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.active = False
        self.logger = logging.getLogger(__name__)
        self.last_content = ""
        
    def set_active(self, active):
        """Enable or disable monitoring."""
        self.active = active
        if not active and self.isRunning():
            self.terminate()
    
    def run(self):
        """Monitor active window continuously."""
        try:
            self.status.emit("Starting continuous monitoring of active window...")
            
            while self.active:
                # Capture the active window content
                content = self._capture_active_window()
                
                # Compare with last captured content
                if content and content.strip() and self._content_changed(content):
                    self.content_detected.emit(content)
                    self.status.emit("Content change detected in active window")
                    self.last_content = content
                
                # Wait 5 seconds before next capture
                for _ in range(50):  # Check every 100ms if still active
                    if not self.active:
                        break
                    time.sleep(0.1)
                    
        except Exception as e:
            self.error.emit(str(e))
            self.logger.error(f"Error in screen monitoring: {str(e)}")
            
    def _content_changed(self, new_content):
        """Detect significant content changes."""
        if not new_content.strip() or not self.last_content.strip():
            return new_content.strip() and not self.last_content.strip()
            
        # Simple diff check
        words1 = set(self.last_content.split())
        words2 = set(new_content.split())
        
        # Check for significant difference
        if len(words1) == 0:
            return len(words2) > 5
        
        difference = len(words1.symmetric_difference(words2))
        return difference / len(words1) > 0.3  # 30% change threshold
            
    def _capture_active_window(self):
        """Capture the active window based on platform."""
        if sys.platform == "darwin":  # macOS
            return self._capture_active_window_mac()
        elif sys.platform == "win32":  # Windows
            return self._capture_active_window_windows()
        else:  # Linux and others
            return self._capture_active_window_linux()
            
    def _capture_active_window_mac(self):
        """Capture active window on macOS."""
        try:
            # Create a temporary file for the screenshot
            fd, temp_path = tempfile.mkstemp('.png')
            os.close(fd)
            
            # Take screenshot of the active window 
            # macOS screencapture -w captures the active window
            subprocess.call(['screencapture', '-w', temp_path])
            
            # Open the image and process with OCR
            from PIL import Image
            import pytesseract
            
            # Check if file exists and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                screenshot = Image.open(temp_path)
                content = pytesseract.image_to_string(screenshot)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                return content
            else:
                self.status.emit("Failed to capture active window or no window selected")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error capturing active window: {str(e)}")
            return ""
            
    def _capture_active_window_windows(self):
        """Capture active window on Windows."""
        try:
            import pyautogui
            from PIL import ImageGrab
            import win32gui
            import win32con
            import pytesseract
            
            # Get the handle of the foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get the window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            
            # Capture the window
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Process with OCR
            content = pytesseract.image_to_string(screenshot)
            
            return content
                
        except Exception as e:
            self.logger.error(f"Error capturing active window: {str(e)}")
            return ""
            
    def _capture_active_window_linux(self):
        """Capture active window on Linux."""
        try:
            # Create a temporary file for the screenshot
            fd, temp_path = tempfile.mkstemp('.png')
            os.close(fd)
            
            # Use xdotool and import to capture the active window
            # First, get the active window ID
            window_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
            
            # Then capture the window
            subprocess.call(['import', '-window', window_id, temp_path])
            
            # Open the image and process with OCR
            from PIL import Image
            import pytesseract
            
            # Check if file exists and has content
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                screenshot = Image.open(temp_path)
                content = pytesseract.image_to_string(screenshot)
                
                # Clean up temporary file
                os.unlink(temp_path)
                
                return content
            else:
                self.status.emit("Failed to capture active window")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error capturing active window: {str(e)}")
            return "" 