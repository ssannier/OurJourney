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
# CONSTANTS CONFIGURATION
# ============================================================================

API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")
if not API_GATEWAY_URL:
    raise ValueError("API_GATEWAY_URL environment variable is required")


KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
if not KNOWLEDGE_BASE_ID:
    raise ValueError("KNOWLEDGE_BASE_ID environment variable is required")