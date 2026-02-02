import os
import logging

"""
Constants for Amplify CloudFormation Custom Resource
This module contains configuration constants used throughout the application
"""

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Logging configuration - change LOG_LEVEL to control all modules
LOG_LEVEL = logging.INFO  # or logging.DEBUG, logging.WARNING, etc.
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
# CLOUDFORMATION RESPONSE CONSTANTS
# ============================================================================
# CloudFormation custom resource response statuses
CFN_SUCCESS = "SUCCESS"
CFN_FAILED = "FAILED"

# Standard response messages
RESPONSE_MESSAGES = {
    "CREATE_SUCCESS": "Create operation completed successfully",
    "UPDATE_SUCCESS": "Update operation completed successfully", 
    "DELETE_SUCCESS": "Delete operation completed successfully",
    "GENERIC_SUCCESS": "operation completed successfully",
    "ENV_VAR_MISSING": "Required environment variable is not set",
    "APP_ID_NOT_FOUND": "No appId available, cannot proceed with operation",
    "ZIP_EXTRACTION_ERROR": "Error extracting zip file from S3 bucket",
    "APP_ID_SAVE_ERROR": "Error saving app ID to S3",
    "APP_ID_RETRIEVE_ERROR": "Error retrieving app ID from S3",
    "APP_ID_FILE_NOT_FOUND": "App ID file not found in S3"
}

# ============================================================================
# ENVIRONMENT VARIABLE VALIDATION
# ============================================================================
# Required environment variables with validation
AMPLIFY_APP_NAME = os.environ.get("AMPLIFY_APP_NAME")
if not AMPLIFY_APP_NAME:
    raise ValueError("AMPLIFY_APP_NAME environment variable is required")

FRONTEND_BUCKET_NAME = os.environ.get("FRONTEND_BUCKET_NAME")
if not FRONTEND_BUCKET_NAME:
    raise ValueError("FRONTEND_BUCKET_NAME environment variable is required")

FRONTEND_FOLDER_NAME = os.environ.get("FRONTEND_FOLDER_NAME")
if not FRONTEND_FOLDER_NAME:
    raise ValueError("FRONTEND_FOLDER_NAME environment variable is required")

# ============================================================================
# AMPLIFY CONFIGURATION CONSTANTS
# ============================================================================
# Default Amplify app configuration
AMPLIFY_APP_CONFIG = {
    "description": "ASU NLQ Chatbot Amplify App",
    "platform": "WEB",
    "enableBranchAutoBuild": False,
    "enableBranchAutoDeletion": False,
    "enableBasicAuth": False,
    "enableAutoBranchCreation": False,
    "customHeaders": ""
}

# Custom rules for SPA routing
AMPLIFY_CUSTOM_RULES = [
    {
        "source": "/<*>",
        "target": "/index.html", 
        "status": "404-200"
    }
]

# Default branch configuration
AMPLIFY_BRANCH_CONFIG = {
    "branchName": "prod",
    "description": "Production branch for ASU NLQ Chatbot",
    "stage": "PRODUCTION",
    "enableNotification": False,
    "enableAutoBuild": True,
    "enableBasicAuth": False,
    "enablePerformanceMode": False,
    "ttl": "5",
    "enablePullRequestPreview": False,
    "backend": {}
}

# Deployment configuration
AMPLIFY_DEPLOYMENT_CONFIG = {
    "sourceUrlType": "BUCKET_PREFIX"
}

# ============================================================================
# S3 CONFIGURATION CONSTANTS
# ============================================================================
# Default zip file name to extract
DEFAULT_ZIP_FILE = "build.zip"

# S3 batch delete limit (AWS maximum)
S3_DELETE_BATCH_SIZE = 1000

# App ID storage configuration
APP_ID_FILE_NAME = "amplify-app-id.txt"
APP_ID_FILE_KEY = f"{FRONTEND_FOLDER_NAME.rstrip('/')}/{APP_ID_FILE_NAME}"