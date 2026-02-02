#!/bin/bash

################################################################################
# Bedrock Knowledge Base Preparation Script
# 
# Usage:
#   ./bedrock.sh <KNOWLEDGE_BASE_ID> <DOC_BUCKET_NAME> <SOURCE_DIR>
#
# This script:
#   1. Validates the source directory contains documents
#   2. Uploads documents to the S3 bucket
#   3. Retrieves the data source ID
#   4. Starts a Knowledge Base ingestion job
#   5. Waits for ingestion to complete
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
AWS_REGION="us-east-1"
KNOWLEDGE_BASE_ID=""
DOC_BUCKET_NAME=""
SOURCE_DIR=""
DATA_SOURCE_ID=""
INGESTION_JOB_ID=""

################################################################################
# Utility Functions
################################################################################

print_substep() {
    echo -e "    ${BLUE}├─${NC} $1" >&2
}

print_error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1" >&2
}

################################################################################
# Rollback Function
################################################################################

rollback() {
    echo "" >&2
    print_error "Knowledge Base preparation failed, performing rollback..."
    
    # Remove uploaded documents from S3 bucket
    if [ -n "$DOC_BUCKET_NAME" ]; then
        print_substep "Removing uploaded documents from S3..."
        aws s3 rm s3://${DOC_BUCKET_NAME}/ --recursive --region ${AWS_REGION} 2>/dev/null || true
        print_substep "S3 bucket cleaned"
    fi
    
    print_substep "Rollback completed"
    exit 1
}

################################################################################
# Validation Functions
################################################################################

validate_source_directory() {
    print_substep "Validating source directory: $SOURCE_DIR"
    
    # Check if directory exists
    if [ ! -d "$SOURCE_DIR" ]; then
        print_error "Source directory not found: $SOURCE_DIR"
        exit 1
    fi
    
    # Count files in directory
    FILE_COUNT=$(find "$SOURCE_DIR" -type f | wc -l | tr -d ' ')
    
    if [ "$FILE_COUNT" -eq 0 ]; then
        print_error "No files found in source directory: $SOURCE_DIR"
        exit 1
    fi
    
    print_substep "Found $FILE_COUNT document(s) to upload"
}

################################################################################
# S3 Upload Functions
################################################################################

upload_documents_to_s3() {
    print_substep "Uploading documents to S3 bucket: $DOC_BUCKET_NAME"
    
    # Perform S3 sync
    if ! aws s3 sync "$SOURCE_DIR" "s3://${DOC_BUCKET_NAME}/" --region ${AWS_REGION} >&2; then
        print_error "Failed to upload documents to S3"
        rollback
    fi
    
    # Verify upload by listing bucket contents
    UPLOADED_COUNT=$(aws s3 ls "s3://${DOC_BUCKET_NAME}/" --recursive --region ${AWS_REGION} | wc -l | tr -d ' ')
    
    if [ "$UPLOADED_COUNT" -eq 0 ]; then
        print_error "S3 bucket is empty after upload"
        rollback
    fi
    
    print_substep "Documents uploaded successfully ($UPLOADED_COUNT files)"
}

################################################################################
# Knowledge Base Ingestion Functions
################################################################################

get_data_source_id() {
    print_substep "Retrieving data source ID..."
    
    DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources \
        --knowledge-base-id ${KNOWLEDGE_BASE_ID} \
        --region ${AWS_REGION} \
        --query 'dataSourceSummaries[0].dataSourceId' \
        --output text 2>/dev/null)
    
    if [ -z "$DATA_SOURCE_ID" ] || [ "$DATA_SOURCE_ID" == "None" ]; then
        print_error "Failed to retrieve data source ID"
        rollback
    fi
    
    print_substep "Data source ID: $DATA_SOURCE_ID"
}

start_ingestion_job() {
    print_substep "Starting ingestion job..."
    
    INGESTION_JOB_ID=$(aws bedrock-agent start-ingestion-job \
        --knowledge-base-id ${KNOWLEDGE_BASE_ID} \
        --data-source-id ${DATA_SOURCE_ID} \
        --region ${AWS_REGION} \
        --query 'ingestionJob.ingestionJobId' \
        --output text 2>/dev/null)
    
    if [ -z "$INGESTION_JOB_ID" ] || [ "$INGESTION_JOB_ID" == "None" ]; then
        print_error "Failed to start ingestion job"
        rollback
    fi
    
    print_substep "Ingestion job started: $INGESTION_JOB_ID"
}

wait_for_ingestion() {
    print_substep "Waiting for Knowledge Base ingestion to complete..."
    
    while true; do
        # Get ingestion job status
        STATUS=$(aws bedrock-agent get-ingestion-job \
            --knowledge-base-id ${KNOWLEDGE_BASE_ID} \
            --data-source-id ${DATA_SOURCE_ID} \
            --ingestion-job-id ${INGESTION_JOB_ID} \
            --region ${AWS_REGION} \
            --query 'ingestionJob.status' \
            --output text 2>/dev/null)
        
        case $STATUS in
            COMPLETE)
                print_substep "Knowledge Base ingestion completed successfully"
                return 0
                ;;
            FAILED)
                print_error "Knowledge Base ingestion failed"
                
                # Try to get failure reasons
                FAILURE_REASONS=$(aws bedrock-agent get-ingestion-job \
                    --knowledge-base-id ${KNOWLEDGE_BASE_ID} \
                    --data-source-id ${DATA_SOURCE_ID} \
                    --ingestion-job-id ${INGESTION_JOB_ID} \
                    --region ${AWS_REGION} \
                    --query 'ingestionJob.failureReasons' \
                    --output text 2>/dev/null)
                
                if [ -n "$FAILURE_REASONS" ] && [ "$FAILURE_REASONS" != "None" ]; then
                    print_error "Failure reasons: $FAILURE_REASONS"
                fi
                
                rollback
                ;;
            STARTING|IN_PROGRESS)
                # Continue waiting
                sleep 10
                ;;
            *)
                print_error "Unknown ingestion status: $STATUS"
                rollback
                ;;
        esac
    done
}

################################################################################
# Main Function
################################################################################

main() {
    # Check if all required arguments are provided
    if [ $# -ne 3 ]; then
        print_error "Invalid number of arguments"
        echo "Usage: $0 <KNOWLEDGE_BASE_ID> <DOC_BUCKET_NAME> <SOURCE_DIR>" >&2
        exit 1
    fi
    
    KNOWLEDGE_BASE_ID=$1
    DOC_BUCKET_NAME=$2
    SOURCE_DIR=$3
    
    # Validate inputs
    if [ -z "$KNOWLEDGE_BASE_ID" ]; then
        print_error "Knowledge Base ID cannot be empty"
        exit 1
    fi
    
    if [ -z "$DOC_BUCKET_NAME" ]; then
        print_error "Document bucket name cannot be empty"
        exit 1
    fi
    
    if [ -z "$SOURCE_DIR" ]; then
        print_error "Source directory cannot be empty"
        exit 1
    fi
    
    # Step 1: Validate source directory
    validate_source_directory
    
    # Step 2: Upload documents to S3
    upload_documents_to_s3
    
    # Step 3: Get data source ID
    get_data_source_id
    
    # Step 4: Start ingestion job
    start_ingestion_job
    
    # Step 5: Wait for ingestion to complete
    wait_for_ingestion
    
    # Success!
    exit 0
}

# Run main function
main "$@"