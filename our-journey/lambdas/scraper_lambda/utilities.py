import json
import logging
import traceback
import time
import hashlib
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import urllib3
import boto3
import requests
from bs4 import BeautifulSoup
from constants import *

# Configure logging
logger = logging.getLogger(__name__)

# Initialize HTTP client for CloudFormation responses
http = urllib3.PoolManager()

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_agent_client = boto3.client('bedrock-agent', region_name=AWS_REGION)


# ============================================================================
# CLOUDFORMATION RESPONSE HANDLER
# ============================================================================

def send_cfn_response(event, context, response_status, response_data, physical_resource_id=None, no_echo=False, reason=None):
    """
    Send response back to CloudFormation service.
    Constructs and sends the required response format for CloudFormation
    custom resources using the pre-signed URL from the event.
    
    Args:
        event: CloudFormation event data containing ResponseURL
        context: Lambda context object
        response_status (str): SUCCESS or FAILED
        response_data (dict): Custom data to return
        physical_resource_id (str, optional): Resource identifier
        no_echo (bool, optional): Whether to mask the response
        reason (str, optional): Custom reason for the response
    """
    logger.info(f"Sending CloudFormation response: {response_status}")
    try:
        response_url = event['ResponseURL']
        response_body = {
            'Status': response_status,
            'Reason': reason or f"See CloudWatch Log Stream: {context.log_stream_name}",
            'PhysicalResourceId': physical_resource_id or context.log_stream_name,
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'NoEcho': no_echo,
            'Data': response_data
        }
        
        json_response_body = json.dumps(response_body)
        logger.debug(f"Response body: {json_response_body}")
        
        headers = {
            'content-type': '',
            'content-length': str(len(json_response_body))
        }
        
        response = http.request('PUT', response_url, headers=headers, body=json_response_body)
        logger.info(f"CloudFormation response sent successfully: {response.status}")
        
    except Exception as e:
        logger.error(f"Failed to send CloudFormation response: {str(e)}")
        # Don't re-raise - we don't want the Lambda to fail if CFN response fails


# ============================================================================
# CLOUDFORMATION EVENT HANDLERS
# ============================================================================

def handle_create_request(event, context):
    """
    Handle CloudFormation CREATE request.
    Executes full scrape and sync operation, then sends response to CloudFormation.
    """
    logger.info("Handling CREATE request - starting scrape and sync")
    
    try:
        # Execute the scraping and sync operation
        result = scrape_and_sync(event, context, is_custom_resource=True)
        
        # Send success response to CloudFormation
        logger.info("CREATE operation completed successfully")
        send_cfn_response(
            event, 
            context, 
            CFN_SUCCESS, 
            {
                "Message": RESPONSE_MESSAGES["CREATE_SUCCESS"],
                "PagesScraped": result.get("pages_scraped", 0),
                "PDFsDownloaded": result.get("pdfs_downloaded", 0),
                "IngestionStatus": result.get("ingestion_status", "UNKNOWN")
            }
        )
        
    except Exception as e:
        error_msg = f"CREATE request failed: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        # Send success anyway to prevent stack from hanging
        send_cfn_response(
            event,
            context,
            CFN_SUCCESS,
            {
                "Message": "CREATE completed with errors",
                "Error": error_msg
            }
        )


def handle_update_request(event, context):
    """
    Handle CloudFormation UPDATE request.
    No-op since weekly EventBridge schedule handles updates.
    """
    logger.info("Handling UPDATE request - no-op (EventBridge handles weekly updates)")
    
    send_cfn_response(
        event,
        context,
        CFN_SUCCESS,
        {
            "Message": RESPONSE_MESSAGES["UPDATE_SUCCESS"],
            "Note": "Weekly updates are handled by EventBridge schedule"
        }
    )


def handle_delete_request(event, context):
    """
    Handle CloudFormation DELETE request.
    No-op since S3 bucket has auto-delete enabled.
    """
    logger.info("Handling DELETE request - no-op (bucket has auto-delete policy)")
    
    send_cfn_response(
        event,
        context,
        CFN_SUCCESS,
        {
            "Message": RESPONSE_MESSAGES["DELETE_SUCCESS"],
            "Note": "S3 bucket has auto-delete policy enabled"
        }
    )


# ============================================================================
# MAIN ORCHESTRATION FUNCTION
# ============================================================================

def scrape_and_sync(event, context, is_custom_resource=False):
    """
    Main orchestration function for scraping and syncing Knowledge Base.
    Called by both Custom Resource CREATE and EventBridge scheduled events.
    
    Args:
        event: Lambda event (CloudFormation or EventBridge)
        context: Lambda context object
        is_custom_resource: Whether this is a Custom Resource invocation
        
    Returns:
        dict: Summary of operation (pages scraped, PDFs downloaded, ingestion status)
    """
    logger.info("=" * 80)
    logger.info("Starting scrape and sync operation")
    logger.info("=" * 80)
    
    result = {
        "pages_scraped": 0,
        "pdfs_downloaded": 0,
        "ingestion_status": "NOT_STARTED"
    }
    
    try:
        # Step 1: Clear S3 bucket
        logger.info("Step 1: Clearing S3 bucket")
        clear_s3_bucket()
        logger.info("✓ S3 bucket cleared successfully")
        
        # Step 2: Scrape HTML pages
        logger.info("Step 2: Scraping HTML pages")
        pages_scraped = scrape_html_pages()
        result["pages_scraped"] = pages_scraped
        logger.info(f"✓ Scraped {pages_scraped} HTML pages")
        
        # Step 3: Discover and download PDFs
        logger.info("Step 3: Discovering and downloading PDFs")
        pdfs_downloaded = discover_and_download_pdfs()
        result["pdfs_downloaded"] = pdfs_downloaded
        logger.info(f"✓ Downloaded {pdfs_downloaded} PDF files")
        
        # Step 4: Start Knowledge Base ingestion
        logger.info("Step 4: Starting Knowledge Base ingestion")
        success, job_id, data_source_id = start_kb_ingestion()
        
        if not success:
            logger.error("Failed to start ingestion job")
            result["ingestion_status"] = "FAILED_TO_START"
            return result
        
        logger.info(f"✓ Ingestion job started: {job_id}")
        result["ingestion_status"] = "STARTED"
        
        # Step 5: Wait for ingestion (with timeout awareness)
        remaining_time = get_remaining_time_seconds(context)
        logger.info(f"Step 5: Waiting for ingestion (remaining time: {remaining_time:.0f}s)")
        
        if remaining_time < LAMBDA_TIMEOUT_BUFFER:
            logger.warning(f"Not enough time to wait for ingestion ({remaining_time:.0f}s < {LAMBDA_TIMEOUT_BUFFER}s buffer)")
            logger.info("Ingestion job will complete asynchronously")
            result["ingestion_status"] = "TIMEOUT_GRACEFUL"
            return result
        
        ingestion_result = wait_for_ingestion(job_id, data_source_id, context)
        result["ingestion_status"] = ingestion_result["status"]
        
        if ingestion_result["status"] == "COMPLETE":
            logger.info("✓ Knowledge Base ingestion completed successfully")
        elif ingestion_result["status"] == "TIMEOUT_GRACEFUL":
            logger.info("✓ Ingestion started successfully, completing without waiting")
        else:
            logger.error(f"Ingestion ended with status: {ingestion_result['status']}")
        
        logger.info("=" * 80)
        logger.info("Scrape and sync operation completed")
        logger.info(f"Summary: {result}")
        logger.info("=" * 80)
        
        return result
        
    except Exception as e:
        error_msg = f"Error in scrape and sync: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        raise


# ============================================================================
# S3 OPERATIONS
# ============================================================================

def clear_s3_bucket():
    """
    Clear all objects from the document bucket.
    Deletes in batches to handle large numbers of files.
    """
    logger.info(f"Clearing bucket: {DOC_BUCKET_NAME}")
    
    try:
        # List all objects
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=DOC_BUCKET_NAME)
        
        delete_count = 0
        
        for page in pages:
            if 'Contents' not in page:
                continue
            
            # Prepare objects for deletion
            objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
            
            # Delete in batches
            for i in range(0, len(objects_to_delete), S3_DELETE_BATCH_SIZE):
                batch = objects_to_delete[i:i + S3_DELETE_BATCH_SIZE]
                
                response = s3_client.delete_objects(
                    Bucket=DOC_BUCKET_NAME,
                    Delete={'Objects': batch}
                )
                
                deleted = len(response.get('Deleted', []))
                delete_count += deleted
                logger.debug(f"Deleted batch of {deleted} objects")
        
        logger.info(f"Cleared {delete_count} objects from bucket")
        
    except Exception as e:
        error_msg = f"Error clearing S3 bucket: {str(e)}"
        logger.error(error_msg)
        raise


# ============================================================================
# WEB SCRAPING FUNCTIONS
# ============================================================================

def scrape_html_pages():
    """
    Scrape all HTML pages from SCRAPER_URLS and upload to S3.
    
    Returns:
        int: Number of successfully scraped pages
    """
    logger.info(f"Scraping {len(SCRAPER_URLS)} HTML pages")
    success_count = 0
    
    for filename, url in SCRAPER_URLS.items():
        try:
            logger.info(f"Scraping: {url}")
            
            # Fetch HTML
            response = requests.get(url, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            
            # Extract content
            text_content = extract_main_content(response.content, url, filename)
            
            # Upload to S3
            upload_text_to_s3(filename, text_content)
            
            success_count += 1
            logger.info(f"✓ Successfully scraped and uploaded: {filename}")
            
            # Be polite - wait between requests
            time.sleep(PAGE_SCRAPE_DELAY)
            
        except Exception as e:
            logger.error(f"✗ Failed to scrape {url}: {str(e)}")
            # Continue with other pages
    
    return success_count


def extract_main_content(html_content, url, page_name):
    """
    Extract main content from HTML page.
    
    Args:
        html_content: Raw HTML bytes
        url: Source URL
        page_name: Name for the page
        
    Returns:
        str: Formatted text content with metadata header
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()
    
    # Extract page title
    title = soup.find('title')
    title_text = title.get_text(strip=True) if title else page_name.replace('-', ' ').title()
    
    # Find main content area
    main_content = soup.find('main') or soup.find('article') or soup.find('body')
    
    if not main_content:
        return ""
    
    # Extract text
    text = main_content.get_text(separator='\n', strip=True)
    
    # Clean up whitespace
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    content_text = '\n'.join(cleaned_lines)
    
    # Create output with metadata header
    output = f"""Source: {url}
Title: {title_text}
Scraped: {datetime.now().strftime('%Y-%m-%d')}

{content_text}"""
    
    return output


def discover_and_download_pdfs():
    """
    Discover PDF links from the reentry resource guides page and download them.
    
    Returns:
        int: Number of successfully downloaded PDFs
    """
    logger.info(f"Discovering PDFs from: {PDF_SOURCE_URL}")
    
    try:
        # Fetch the page containing PDF links
        response = requests.get(PDF_SOURCE_URL, headers=HTTP_HEADERS, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        
        # Discover PDF links
        pdf_links = discover_pdf_links(response.content, PDF_SOURCE_URL)
        logger.info(f"Found {len(pdf_links)} PDF link(s)")
        
        if not pdf_links:
            logger.warning("No PDF links found")
            return 0
        
        # Download each PDF
        success_count = 0
        for i, pdf_url in enumerate(pdf_links, 1):
            try:
                logger.info(f"[{i}/{len(pdf_links)}] Downloading PDF: {pdf_url}")
                
                success, filename, content = download_pdf(pdf_url)
                
                if success:
                    upload_pdf_to_s3(filename, content)
                    success_count += 1
                    logger.info(f"✓ Downloaded and uploaded: {filename}")
                
                # Be polite - wait between downloads
                time.sleep(PDF_DOWNLOAD_DELAY)
                
            except Exception as e:
                logger.error(f"✗ Failed to download PDF {pdf_url}: {str(e)}")
                # Continue with other PDFs
        
        return success_count
        
    except Exception as e:
        logger.error(f"Error in PDF discovery/download: {str(e)}")
        return 0


def discover_pdf_links(html_content, base_url):
    """
    Discover all PDF links on a page.
    
    Args:
        html_content: Raw HTML bytes
        base_url: Base URL for resolving relative links
        
    Returns:
        list: List of absolute PDF URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    pdf_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        
        # Check if it's a PDF link
        if href.lower().endswith('.pdf'):
            # Convert to absolute URL
            absolute_url = urljoin(base_url, href)
            pdf_links.append(absolute_url)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_pdfs = []
    for pdf_url in pdf_links:
        if pdf_url not in seen:
            seen.add(pdf_url)
            unique_pdfs.append(pdf_url)
    
    return unique_pdfs


def download_pdf(url):
    """
    Download a PDF file from a URL.
    
    Args:
        url: PDF URL to download
        
    Returns:
        tuple: (success: bool, filename: str, content: bytes)
    """
    try:
        # Generate filename
        filename = create_filename_from_url(url)
        
        # Download PDF
        response = requests.get(url, headers=HTTP_HEADERS, timeout=PDF_TIMEOUT, stream=True)
        response.raise_for_status()
        
        # Read content
        content = response.content
        file_size_kb = len(content) / 1024
        
        logger.debug(f"Downloaded {filename} ({file_size_kb:.1f} KB)")
        
        return True, filename, content
        
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        return False, None, None


# ============================================================================
# S3 UPLOAD FUNCTIONS
# ============================================================================

def upload_text_to_s3(filename, text_content):
    """
    Upload text content to S3 bucket.
    
    Args:
        filename: Base filename (without extension)
        text_content: Text content to upload
    """
    key = f"{filename}{TEXT_FILE_SUFFIX}"
    
    s3_client.put_object(
        Bucket=DOC_BUCKET_NAME,
        Key=key,
        Body=text_content.encode('utf-8'),
        ContentType='text/plain'
    )
    
    logger.debug(f"Uploaded text file: {key}")


def upload_pdf_to_s3(filename, pdf_bytes):
    """
    Upload PDF content to S3 bucket.
    
    Args:
        filename: Filename (should include .pdf extension)
        pdf_bytes: PDF binary content
    """
    # Ensure filename has .pdf extension
    if not filename.endswith(PDF_FILE_SUFFIX):
        filename = f"{filename}{PDF_FILE_SUFFIX}"
    
    key = filename
    
    s3_client.put_object(
        Bucket=DOC_BUCKET_NAME,
        Key=key,
        Body=pdf_bytes,
        ContentType='application/pdf'
    )
    
    file_size_kb = len(pdf_bytes) / 1024
    logger.debug(f"Uploaded PDF: {key} ({file_size_kb:.1f} KB)")


# ============================================================================
# BEDROCK KNOWLEDGE BASE OPERATIONS
# ============================================================================

def start_kb_ingestion():
    """
    Start Knowledge Base ingestion job.
    
    Returns:
        tuple: (success: bool, job_id: str, data_source_id: str)
    """
    try:
        # Get data source ID
        data_source_id = get_data_source_id()
        logger.info(f"Data source ID: {data_source_id}")
        
        # Start ingestion job
        response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            dataSourceId=data_source_id
        )
        
        job_id = response['ingestionJob']['ingestionJobId']
        logger.info(f"Started ingestion job: {job_id}")
        
        return True, job_id, data_source_id
        
    except Exception as e:
        logger.error(f"Error starting ingestion job: {str(e)}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        return False, None, None


def get_data_source_id():
    """
    Get the data source ID for the Knowledge Base.
    
    Returns:
        str: Data source ID
    """
    try:
        response = bedrock_agent_client.list_data_sources(
            knowledgeBaseId=KNOWLEDGE_BASE_ID
        )
        
        data_sources = response.get('dataSourceSummaries', [])
        
        if not data_sources:
            raise ValueError(f"No data sources found for Knowledge Base: {KNOWLEDGE_BASE_ID}")
        
        # Return the first data source ID
        data_source_id = data_sources[0]['dataSourceId']
        return data_source_id
        
    except Exception as e:
        logger.error(f"Error getting data source ID: {str(e)}")
        raise


def wait_for_ingestion(job_id, data_source_id, context):
    """
    Wait for Knowledge Base ingestion job to complete.
    Polls status and checks for timeout.
    
    Args:
        job_id: Ingestion job ID
        data_source_id: Data source ID
        context: Lambda context for timeout checking
        
    Returns:
        dict: Ingestion result with status and details
    """
    logger.info(f"Waiting for ingestion job to complete: {job_id}")
    
    start_time = time.time()
    
    while True:
        try:
            # Check remaining Lambda time
            remaining_time = get_remaining_time_seconds(context)
            
            if remaining_time < LAMBDA_TIMEOUT_BUFFER:
                logger.warning(f"Approaching Lambda timeout ({remaining_time:.0f}s remaining)")
                logger.info("Returning gracefully - ingestion will complete asynchronously")
                return {
                    "status": "TIMEOUT_GRACEFUL",
                    "message": "Ingestion started but not completed within Lambda timeout"
                }
            
            # Check if we've exceeded max wait time
            elapsed_time = time.time() - start_time
            if elapsed_time > INGESTION_MAX_WAIT_TIME:
                logger.warning(f"Exceeded max wait time ({INGESTION_MAX_WAIT_TIME}s)")
                return {
                    "status": "TIMEOUT_GRACEFUL",
                    "message": "Ingestion started but exceeded max wait time"
                }
            
            # Get job status
            response = bedrock_agent_client.get_ingestion_job(
                knowledgeBaseId=KNOWLEDGE_BASE_ID,
                dataSourceId=data_source_id,
                ingestionJobId=job_id
            )
            
            status = response['ingestionJob']['status']
            logger.debug(f"Ingestion status: {status} (elapsed: {elapsed_time:.0f}s)")
            
            if status == INGESTION_STATUS_COMPLETE:
                logger.info("Ingestion completed successfully")
                return {
                    "status": "COMPLETE",
                    "elapsed_time": elapsed_time
                }
            
            elif status == INGESTION_STATUS_FAILED:
                failure_reasons = response['ingestionJob'].get('failureReasons', [])
                logger.error(f"Ingestion failed: {failure_reasons}")
                return {
                    "status": "FAILED",
                    "failure_reasons": failure_reasons
                }
            
            elif status in [INGESTION_STATUS_STARTING, INGESTION_STATUS_IN_PROGRESS]:
                # Continue waiting
                time.sleep(INGESTION_POLL_INTERVAL)
            
            else:
                logger.warning(f"Unknown ingestion status: {status}")
                return {
                    "status": "UNKNOWN",
                    "raw_status": status
                }
        
        except Exception as e:
            logger.error(f"Error checking ingestion status: {str(e)}")
            raise


# ============================================================================
# UTILITY HELPERS
# ============================================================================

def get_remaining_time_seconds(context):
    """
    Get remaining Lambda execution time in seconds.
    
    Args:
        context: Lambda context object
        
    Returns:
        float: Remaining time in seconds
    """
    return context.get_remaining_time_in_millis() / 1000.0


def create_filename_from_url(url):
    """
    Create a filename from a URL.
    Extracts filename from URL path, or generates one from hash if needed.
    
    Args:
        url: URL to extract filename from
        
    Returns:
        str: Clean filename
    """
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    
    # If no good filename, create one from URL hash
    if not filename or filename == '.pdf':
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"resource_{url_hash}.pdf"
    
    return filename