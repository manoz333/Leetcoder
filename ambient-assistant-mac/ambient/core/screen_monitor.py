import time
from PIL import ImageGrab
import pytesseract
from ambient.core.event_bus import Events
import logging
import re
from typing import Dict, Any

class ScreenMonitor:
    def __init__(self, event_bus, settings_manager):
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        self.last_content = ""
        self.running = False
        
        # Common code file extensions
        self.code_extensions = {
            'python': ['.py', '.ipynb'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.hpp', '.cc'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss'],
            'rust': ['.rs'],
            'go': ['.go'],
            # Add more as needed
        }
        
    def _detect_context_type(self, content: str) -> Dict[str, Any]:
        """
        Detect the type of content and context from screen text.
        Returns context information including type and relevant details.
        """
        context = {
            "type": "general",
            "details": {},
            "timestamp": time.time()
        }
        
        # Check for code patterns
        code_patterns = {
            'function_def': r'(def|function|class|\w+\s+\w+\([^)]*\)\s*{)',
            'variable_dec': r'(var|let|const|int|float|string|bool)\s+\w+\s*=',
            'imports': r'(import|from|require|using|include)',
            'loops': r'(for|while|do)',
            'conditions': r'(if|else|switch|case)'
        }
        
        code_matches = sum(1 for pattern in code_patterns.values() 
                         if re.search(pattern, content, re.MULTILINE))
        
        if code_matches >= 2:  # If multiple code patterns found
            context["type"] = "code"
            # Detect programming language
            for lang, patterns in self._get_language_patterns().items():
                if any(pattern in content for pattern in patterns):
                    context["details"]["language"] = lang
                    break
                    
        # Check for documentation/comment patterns
        elif '/**' in content or '"""' in content or '#' in content:
            context["type"] = "documentation"
            
        # Check for natural language writing
        elif len(content.split()) > 20:  # If significant text present
            context["type"] = "text"
            
        # Check for UI/drawing tools patterns
        elif any(term in content.lower() for term in ['px', 'rgb', 'rgba', 'stroke', 'fill']):
            context["type"] = "design"
            
        context["content"] = content
        return context

    def _get_language_patterns(self) -> Dict[str, list]:
        """Get patterns to identify programming languages."""
        return {
            'python': ['def ', 'import ', 'class ', ':'],
            'javascript': ['function', 'const', 'let', 'var'],
            'java': ['public class', 'private', 'protected'],
            'cpp': ['#include', 'std::', 'cout'],
            'sql': ['SELECT', 'FROM', 'WHERE'],
            # Add more languages as needed
        }

    def start_monitoring(self):
        """Start continuous screen monitoring."""
        self.running = True
        self.logger.info("Starting screen monitoring")
        
        while self.running:
            try:
                # Capture screen
                screenshot = ImageGrab.grab()
                current_content = pytesseract.image_to_string(screenshot)
                
                if self._content_changed(current_content):
                    # Detect context and type of content
                    context_data = self._detect_context_type(current_content)
                    
                    # Publish content change event with context
                    self.event_bus.publish(Events.CONTEXT_UPDATED, context_data)
                    self.last_content = current_content
                
                # Wait for next capture
                interval = self.settings_manager.get_setting("SCREEN_CAPTURE_INTERVAL")
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in screen monitoring: {e}")
                time.sleep(1)