#!/bin/bash

################################################################################
# Frontend Build Script
# 
# Usage:
#   ./frontend_build.sh <WEBSOCKET_URL>
#
# This script:
#   1. Updates constants.jsx with the WebSocket URL
#   2. Installs npm dependencies
#   3. Builds the frontend application
#   4. Creates build.zip from the dist/ folder
#
# On error, performs rollback to clean state
################################################################################

set -e  # Exit on error
set -o pipefail  # Catch errors in pipes

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="./our-journey-frontend/frontend"
CONSTANTS_FILE="$FRONTEND_DIR/src/app/components/constants.jsx"
CONSTANTS_BACKUP="$FRONTEND_DIR/src/app/components/constants_backup.jsx"
BUILD_DIR="$FRONTEND_DIR/dist"
BUILD_ZIP="./our-journey-frontend/build.zip"
ORIGINAL_DIR=""  # Will be set in main()

################################################################################
# Utility Functions
################################################################################

print_substep() {
    echo -e "    ${BLUE}├─${NC} $1" >&2
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

################################################################################
# Rollback Function
################################################################################

rollback() {
    echo "" >&2
    print_error "Build failed, performing rollback..."
    
    # Restore original constants file
    if [ -f "$CONSTANTS_BACKUP" ]; then
        cp "$CONSTANTS_BACKUP" "$CONSTANTS_FILE" 2>/dev/null || true
        print_substep "Restored constants.jsx from backup"
    fi
    
    # Remove build artifacts
    if [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR" 2>/dev/null || true
        print_substep "Removed dist directory"
    fi
    
    # Remove node_modules
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        rm -rf "$FRONTEND_DIR/node_modules" 2>/dev/null || true
        print_substep "Removed node_modules directory"
    fi
    
    # Remove zip file
    if [ -f "$BUILD_ZIP" ]; then
        rm -f "$BUILD_ZIP" 2>/dev/null || true
        print_substep "Removed build.zip"
    fi
    
    print_substep "Rollback completed"
    exit 1
}

################################################################################
# Main Build Process
################################################################################

main() {
    # Check if WebSocket URL is provided
    if [ $# -eq 0 ]; then
        print_error "WebSocket URL not provided"
        echo "Usage: $0 <WEBSOCKET_URL>" >&2
        exit 1
    fi
    
    # Save the original directory where the script was called from
    ORIGINAL_DIR="$(pwd)"
    
    WEBSOCKET_URL=$1
    
    # Verify backup file exists
    if [ ! -f "$CONSTANTS_BACKUP" ]; then
        print_error "constants_backup.jsx not found at: $CONSTANTS_BACKUP"
        exit 1
    fi
    print_substep "Verified constants_backup.jsx exists"
    
    # Step 1: Restore constants file from backup and update with endpoint
    print_substep "Updating constants.jsx with WebSocket endpoint..."
    
    # Copy backup to constants file
    if ! cp "$CONSTANTS_BACKUP" "$CONSTANTS_FILE"; then
        print_error "Failed to copy constants_backup.jsx to constants.jsx"
        rollback
    fi
    
    # Replace the token with the actual endpoint
    # Using perl for cross-platform compatibility (works on Mac and Linux)
    if command -v perl &> /dev/null; then
        if ! perl -pi -e "s|\"REPLACE_TOKEN\"|\"$WEBSOCKET_URL\"|g" "$CONSTANTS_FILE"; then
            print_error "Failed to update WebSocket URL in constants.jsx"
            rollback
        fi
    else
        # Fallback to sed if perl is not available
        if ! sed -i.tmp "s|\"REPLACE_TOKEN\"|\"$WEBSOCKET_URL\"|g" "$CONSTANTS_FILE"; then
            print_error "Failed to update WebSocket URL in constants.jsx"
            rollback
        fi
        rm -f "$CONSTANTS_FILE.tmp" 2>/dev/null || true
    fi
    
    print_substep "Constants file updated successfully"
    
    # Step 2: Install dependencies
    print_substep "Installing npm dependencies..."
    
    cd "$FRONTEND_DIR" || {
        print_error "Failed to change to frontend directory"
        rollback
    }
    
    if ! npm install; then
        print_error "npm install failed"
        cd "$ORIGINAL_DIR"
        rollback
    fi
    
    print_substep "Dependencies installed successfully"
    
    # Step 3: Build the application
    print_substep "Building application..."
    
    if ! npm run build; then
        print_error "npm run build failed"
        cd "$ORIGINAL_DIR"
        rollback
    fi
    
    print_substep "Application built successfully"
    
    # Check if dist directory exists (we're still in FRONTEND_DIR)
    if [ ! -d "dist" ]; then
        print_error "Build directory 'dist' not found in $(pwd)"
        print_error "Listing current directory:" >&2
        ls -la >&2 || true
        cd "$ORIGINAL_DIR"
        rollback
    fi
    
    print_substep "Build directory verified: dist/"
    
    # Step 4: Create zip archive
    print_substep "Creating deployment archive..."
    
    # We're still in FRONTEND_DIR, get the absolute path to dist
    DIST_ABS="$(pwd)/dist"
    
    # Calculate absolute path for build.zip (should be in our-journey-frontend/)
    # We're in: our-journey-frontend/frontend
    # We want:  our-journey-frontend/build.zip
    BUILD_ZIP_ABS="$(cd .. && pwd)/build.zip"
    
    print_substep "Dist directory: $DIST_ABS" >&2
    print_substep "Build zip will be: $BUILD_ZIP_ABS" >&2
    
    # Remove existing build.zip if it exists
    if [ -f "$BUILD_ZIP_ABS" ]; then
        rm -f "$BUILD_ZIP_ABS" 2>/dev/null || true
        print_substep "Removed existing build.zip" >&2
    fi
    
    # Create the zip from dist directory
    cd "$DIST_ABS" || rollback
    
    print_substep "Creating zip from: $(pwd)" >&2
    if ! zip -r "$BUILD_ZIP_ABS" . 2>&1 | head -5 >&2; then
        print_error "Failed to create build.zip"
        cd "$ORIGINAL_DIR"
        rollback
    fi
    
    # Return to original directory
    cd "$ORIGINAL_DIR"
    
    # Verify zip was created
    if [ ! -f "$BUILD_ZIP_ABS" ]; then
        print_error "build.zip not found at: $BUILD_ZIP_ABS"
        print_error "Current directory: $(pwd)" >&2
        rollback
    fi
    
    # Get zip file size for confirmation
    ZIP_SIZE=$(du -h "$BUILD_ZIP_ABS" | cut -f1)
    print_substep "Deployment archive created successfully ($ZIP_SIZE)"
    
    # Success!
    exit 0
}

# Run main function
main "$@"