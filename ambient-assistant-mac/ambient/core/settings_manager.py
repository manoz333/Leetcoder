import os
import json
import logging
from pathlib import Path

class SettingsManager:
    """Manages application settings with proper error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings_file = self._get_settings_path()
        self.settings = self._load_settings()
        
        # Try to load API keys from environment variables if not in settings
        self._load_env_variables()
        
    def _get_settings_path(self):
        """Get the path to the settings file."""
        # Use user's home directory for settings
        home_dir = str(Path.home())
        app_dir = os.path.join(home_dir, '.ambient_assistant')
        
        # Create directory if it doesn't exist
        if not os.path.exists(app_dir):
            try:
                os.makedirs(app_dir)
            except Exception as e:
                self.logger.error(f"Failed to create settings directory: {e}")
                
        return os.path.join(app_dir, 'settings.json')
    
    def _load_settings(self):
        """Load settings from file with error handling."""
        if not os.path.exists(self.settings_file):
            self.logger.info("Settings file not found, creating default settings")
            return self._create_default_settings()
            
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.logger.info("Settings loaded successfully")
                return settings
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            return self._create_default_settings()
            
    def _load_env_variables(self):
        """Load settings from environment variables."""
        # Try to get OpenAI API key from environment
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if openai_api_key and not self.settings.get('openai_api_key'):
            self.settings['openai_api_key'] = openai_api_key
            self.logger.info("OpenAI API key loaded from environment")
            
        # Also try to load from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            env_api_key = os.getenv('OPENAI_API_KEY')
            if env_api_key and not self.settings.get('openai_api_key'):
                self.settings['openai_api_key'] = env_api_key
                self.logger.info("OpenAI API key loaded from .env file")
        except ImportError:
            pass
            
    def _create_default_settings(self):
        """Create default settings."""
        default_settings = {
            'openai_api_key': '',
            'theme': 'dark',
            'monitoring_interval': 60,
            'window_opacity': 0.85,
            'auto_start': False,
            'voice_enabled': True
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(default_settings, f, indent=4)
                self.logger.info("Default settings created")
        except Exception as e:
            self.logger.error(f"Failed to create default settings: {e}")
            
        return default_settings
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
                self.logger.info("Settings saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
    
    def get_setting(self, key):
        """Get a setting by key."""
        return self.settings.get(key)
    
    def set_setting(self, key, value):
        """Set a setting and save."""
        self.settings[key] = value
        self._save_settings()
        
    def get_all_settings(self):
        """Get all settings."""
        return self.settings.copy()