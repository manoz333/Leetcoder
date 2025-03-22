import logging
import os
import sys
from pathlib import Path

def setup_logging(level=logging.INFO, log_to_file=True):
    """
    Setup logging configuration for the application.
    
    Args:
        level: The logging level (default: INFO)
        log_to_file: Whether to log to a file (default: True)
    """
    # Create logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled)
    if log_to_file:
        # Create logs directory in user's home
        home_dir = str(Path.home())
        log_dir = os.path.join(home_dir, '.ambient_assistant', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Log file path
        log_file = os.path.join(log_dir, 'ambient_assistant.log')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Handle uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        root_logger.error("Uncaught exception", 
                         exc_info=(exc_type, exc_value, exc_traceback))
    
    # Set exception handler
    sys.excepthook = handle_exception
    
    # Log startup message
    root_logger.info("Logging initialized")
    
    return root_logger 