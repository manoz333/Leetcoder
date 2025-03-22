"""Worker thread for processing screenshots."""
import logging
import os
import sys
import tempfile
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal


class ScreenshotWorker(QThread):
    """Worker thread for screenshot capture to avoid UI freezes."""
    finished = pyqtSignal(str)
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def run(self):
        """Capture current active window and extract text using OCR."""
        try:
            from PIL import Image
            import pytesseract
            
            # Platform-specific code to capture the active window
            if sys.platform == "darwin":  # macOS
                self._capture_active_window_mac()
            elif sys.platform == "win32":  # Windows
                self._capture_active_window_windows()
            else:  # Linux and others
                self._capture_active_window_linux()
                
        except ImportError as e:
            self.error.emit(f"Required packages not installed: {str(e)}")
            self.logger.error(f"Import error in screenshot processing: {str(e)}")
        except Exception as e:
            self.error.emit(str(e))
            self.logger.error(f"Error in screenshot processing: {str(e)}")
            
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
                
                if content.strip():
                    self.finished.emit(content)
                else:
                    self.status.emit("No text detected in active window")
            else:
                self.status.emit("Failed to capture active window or no window selected")
                
        except Exception as e:
            self.error.emit(f"Error capturing active window: {str(e)}")
            self.logger.error(f"Error capturing active window: {str(e)}")
            
    def _capture_active_window_windows(self):
        """Capture active window on Windows."""
        try:
            import pyautogui
            from PIL import ImageGrab
            import win32gui
            import win32con
            
            # Get the handle of the foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get the window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            
            # Capture the window
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            
            # Process with OCR
            import pytesseract
            content = pytesseract.image_to_string(screenshot)
            
            if content.strip():
                self.finished.emit(content)
            else:
                self.status.emit("No text detected in active window")
                
        except Exception as e:
            self.error.emit(f"Error capturing active window: {str(e)}")
            self.logger.error(f"Error capturing active window: {str(e)}")
            
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
                
                if content.strip():
                    self.finished.emit(content)
                else:
                    self.status.emit("No text detected in active window")
            else:
                self.status.emit("Failed to capture active window")
                
        except Exception as e:
            self.error.emit(f"Error capturing active window: {str(e)}")
            self.logger.error(f"Error capturing active window: {str(e)}") 