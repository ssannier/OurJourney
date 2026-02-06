import os
import logging

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Logging configuration - change LOG_LEVEL to control all modules
# Available levels: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL
LOG_LEVEL = logging.INFO  # Change this to control what gets logged
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

def setup_logging():
    """Configure logging for the entire application"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        force=True  # Override any existing configuration
    )

# Call setup when constants is imported
setup_logging()

# ============================================================================
# DYNAMODB CONFIGURATION
# ============================================================================

CONVERSATIONS_TABLE = os.environ.get("CONVERSATIONS_TABLE")
if not CONVERSATIONS_TABLE:
    raise ValueError("CONVERSATIONS_TABLE environment variable is required")

FOLLOWUP_TABLE = os.environ.get("FOLLOWUP_TABLE")
if not FOLLOWUP_TABLE:
    raise ValueError("FOLLOWUP_TABLE environment variable is required")

# ============================================================================
# PAGINATION CONFIGURATION
# ============================================================================

# Default number of items to return per request
DEFAULT_LIMIT = 50

# Maximum number of items allowed per request
MAX_LIMIT = 100

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

# Valid conversation flag values
VALID_FLAGS = ['none', 'crisis', 'followup', 'resolved']

# Valid follow-up status values
VALID_STATUSES = ['new', 'in-progress', 'completed']

# Valid priority values
VALID_PRIORITIES = ['normal', 'urgent']

# Valid request type values
VALID_REQUEST_TYPES = ['normal', 'crisis']