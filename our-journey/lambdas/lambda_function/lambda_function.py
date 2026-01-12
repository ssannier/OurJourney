import logging
import boto3
import json
import traceback
import constants  # This configures logging
from orchestration import orchestrate
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


# the main entry point for the AWS Lambda function
def lambda_handler(event, context):
    """
    AWS Lambda handler for processing chatbot requests.
    Handles both synchronous responses and asynchronous background processing.
    """
   
    logger.info("Lambda handler started")
    
    try:
        # Handle background processing mode
        if event.get('background_processing'):
            logger.info("Starting background processing")
            result = orchestrate(event)
            logger.info("Background processing completed")

            return {"statusCode": 200, "body": "Processing completed"}
        
        # Validate required fields for initial request
        if not event:
            logger.error("Empty event received")
            return {"statusCode": 400, "body": "Invalid event"}
        
        # Initiate asynchronous processing
        logger.info("Initiating async processing")
        lambda_client = boto3.client('lambda')
        
        # Create background event
        background_event = event.copy()
        background_event['background_processing'] = True
        
        # Invoke lambda asynchronously for background processing
        response = lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType='Event',
            Payload=json.dumps(background_event)
        )
        
        logger.info(f"Async invocation initiated with status: {response['StatusCode']}")

        return {"statusCode": 202, "body": "Processing initiated"}
        
    except ClientError as e:
        logger.error(f"AWS Client Error: {e}")
        logger.debug(f"ClientError traceback: {traceback.format_exc()}")
        return {"statusCode": 500, "body": "Service error"}
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(f"Unexpected error traceback: {traceback.format_exc()}")
        return {"statusCode": 500, "body": "Internal error"}
    
    