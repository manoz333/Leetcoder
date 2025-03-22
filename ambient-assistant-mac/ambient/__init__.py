"""
Ambient Assistant - An intelligent macOS assistant that provides context-aware assistance.
"""

__version__ = "1.0.0"

# Configure structlog with custom processors for macOS
import os
import sys
import logging
import structlog

# Configure paths for application
APP_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESOURCES_PATH = os.path.join(APP_ROOT, 'resources')
sys.path.insert(0, APP_ROOT)

# Configure logging
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)

# Add timestamp to logs
timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    cache_logger_on_first_use=True,
)

# Create logger for the application
logger = structlog.get_logger("ambient")

# Setup exception handling hooks
def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Let the system handle KeyboardInterrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("Uncaught exception", 
                exc_info=(exc_type, exc_value, exc_traceback))

# Set the exception hook
sys.excepthook = handle_exception

# Initialize environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ambient.django_backend.settings")

logger.info("Ambient Assistant initializing", version=__version__)