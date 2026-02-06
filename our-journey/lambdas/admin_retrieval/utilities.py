import boto3
import logging
import traceback
from datetime import datetime
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
import constants

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS FOR JSON SERIALIZATION
# ============================================================================

def decimal_to_number(obj):
    """
    Recursively convert Decimal objects to int or float for JSON serialization.
    DynamoDB returns numbers as Decimal objects which are not JSON serializable.
    
    Args:
        obj: Object to convert (can be dict, list, Decimal, or any other type)
    
    Returns:
        Object with all Decimal values converted to int or float
    """
    if isinstance(obj, list):
        return [decimal_to_number(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: decimal_to_number(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        # Convert to int if it's a whole number, otherwise float
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
conversations_table = dynamodb.Table(constants.CONVERSATIONS_TABLE)
followup_table = dynamodb.Table(constants.FOLLOWUP_TABLE)


# ============================================================================
# CONVERSATION QUERIES
# ============================================================================

def query_conversations(filters=None, limit=50, start_key=None):
    """
    Query conversations table with optional filters and pagination.
    
    Args:
        filters: Dictionary of filter criteria (flag, userId, county)
        limit: Maximum number of items to return
        start_key: Pagination token from previous query
    
    Returns:
        dict: {items: [...], lastEvaluatedKey: {...} or None}
    """
    logger.info(f"Querying conversations with filters: {filters}, limit: {limit}")
    
    try:
        scan_kwargs = {
            'Limit': limit
        }
        
        # Add pagination token if provided
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        
        # Build filter expression if filters provided
        if filters:
            filter_expressions = []
            
            # Use GSI for flag filter if it's the only/primary filter
            if 'flag' in filters and len(filters) == 1:
                logger.info(f"Using FlagIndex for flag filter: {filters['flag']}")
                response = conversations_table.query(
                    IndexName='FlagIndex',
                    KeyConditionExpression=Key('flag').eq(filters['flag']),
                    Limit=limit,
                    ScanIndexForward=False,  # Sort by timestamp descending (newest first)
                    **({'ExclusiveStartKey': start_key} if start_key else {})
                )
            else:
                # Use scan with filter expressions for multiple filters or non-indexed filters
                if 'flag' in filters:
                    filter_expressions.append(Attr('flag').eq(filters['flag']))
                
                if 'userId' in filters:
                    filter_expressions.append(Attr('userId').eq(filters['userId']))
                
                if 'county' in filters:
                    filter_expressions.append(Attr('county').eq(filters['county']))
                
                # Combine filter expressions with AND
                if filter_expressions:
                    filter_expr = filter_expressions[0]
                    for expr in filter_expressions[1:]:
                        filter_expr = filter_expr & expr
                    scan_kwargs['FilterExpression'] = filter_expr
                
                response = conversations_table.scan(**scan_kwargs)
        else:
            # No filters - scan all
            response = conversations_table.scan(**scan_kwargs)
        
        items = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        logger.info(f"Retrieved {len(items)} conversations")
        
        return {
            'items': items,
            'lastEvaluatedKey': last_evaluated_key
        }
    
    except Exception as e:
        logger.error(f"Failed to query conversations: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


def get_conversation_by_id(conversation_id, timestamp=None):
    """
    Get a specific conversation by ID.
    If timestamp is provided, gets that specific version.
    Otherwise, queries to get the latest version.
    
    Args:
        conversation_id: Conversation identifier
        timestamp: Optional timestamp (sort key)
    
    Returns:
        dict: Conversation object or None if not found
    """
    logger.info(f"Getting conversation: {conversation_id}, timestamp: {timestamp}")
    
    try:
        if timestamp:
            # Get specific version with both keys
            response = conversations_table.get_item(
                Key={
                    'id': conversation_id,
                    'timestamp': timestamp
                }
            )
            item = response.get('Item')
        else:
            # Query to get latest version (most recent timestamp)
            response = conversations_table.query(
                KeyConditionExpression=Key('id').eq(conversation_id),
                ScanIndexForward=False,  # Sort descending (newest first)
                Limit=1
            )
            items = response.get('Items', [])
            item = items[0] if items else None
        
        if item:
            logger.info(f"Found conversation {conversation_id}")
        else:
            logger.warning(f"Conversation {conversation_id} not found")
        
        return item
    
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


def update_conversation_flag(conversation_id, timestamp, new_flag):
    """
    Update the flag status of a conversation.
    
    Args:
        conversation_id: Conversation identifier
        timestamp: Timestamp of the conversation (sort key)
        new_flag: New flag value (none/crisis/followup/resolved)
    
    Returns:
        dict: Updated conversation item
    """
    logger.info(f"Updating conversation {conversation_id} flag to {new_flag}")
    
    try:
        # Validate flag value
        if new_flag not in constants.VALID_FLAGS:
            raise ValueError(f"Invalid flag value: {new_flag}")
        
        response = conversations_table.update_item(
            Key={
                'id': conversation_id,
                'timestamp': timestamp
            },
            UpdateExpression='SET flag = :flag, updatedAt = :updated',
            ExpressionAttributeValues={
                ':flag': new_flag,
                ':updated': datetime.utcnow().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        updated_item = response.get('Attributes')
        logger.info(f"Conversation flag updated successfully")
        
        return updated_item
    
    except Exception as e:
        logger.error(f"Failed to update conversation flag: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


# ============================================================================
# FOLLOW-UP QUERIES
# ============================================================================

def query_followups(filters=None, limit=50, start_key=None):
    """
    Query follow-ups table with optional filters and pagination.
    
    Args:
        filters: Dictionary of filter criteria (status, priority, requestType)
        limit: Maximum number of items to return
        start_key: Pagination token from previous query
    
    Returns:
        dict: {items: [...], lastEvaluatedKey: {...} or None}
    """
    logger.info(f"Querying follow-ups with filters: {filters}, limit: {limit}")
    
    try:
        scan_kwargs = {
            'Limit': limit
        }
        
        # Add pagination token if provided
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        
        # Build filter expression if filters provided
        if filters:
            # Determine if we can use a GSI
            if 'status' in filters and len(filters) == 1:
                logger.info(f"Using StatusIndex for status filter: {filters['status']}")
                response = followup_table.query(
                    IndexName='StatusIndex',
                    KeyConditionExpression=Key('status').eq(filters['status']),
                    Limit=limit,
                    ScanIndexForward=False,  # Sort by timestamp descending (newest first)
                    **({'ExclusiveStartKey': start_key} if start_key else {})
                )
            elif 'priority' in filters and len(filters) == 1:
                logger.info(f"Using PriorityIndex for priority filter: {filters['priority']}")
                response = followup_table.query(
                    IndexName='PriorityIndex',
                    KeyConditionExpression=Key('priority').eq(filters['priority']),
                    Limit=limit,
                    ScanIndexForward=False,  # Sort by timestamp descending (newest first)
                    **({'ExclusiveStartKey': start_key} if start_key else {})
                )
            elif 'requestType' in filters and len(filters) == 1:
                logger.info(f"Using RequestTypeIndex for requestType filter: {filters['requestType']}")
                response = followup_table.query(
                    IndexName='RequestTypeIndex',
                    KeyConditionExpression=Key('requestType').eq(filters['requestType']),
                    Limit=limit,
                    ScanIndexForward=False,  # Sort by timestamp descending (newest first)
                    **({'ExclusiveStartKey': start_key} if start_key else {})
                )
            else:
                # Multiple filters or non-indexed filters - use scan
                filter_expressions = []
                
                if 'status' in filters:
                    filter_expressions.append(Attr('status').eq(filters['status']))
                
                if 'priority' in filters:
                    filter_expressions.append(Attr('priority').eq(filters['priority']))
                
                if 'requestType' in filters:
                    filter_expressions.append(Attr('requestType').eq(filters['requestType']))
                
                if 'assignedTo' in filters:
                    filter_expressions.append(Attr('assignedTo').eq(filters['assignedTo']))
                
                # Combine filter expressions with AND
                if filter_expressions:
                    filter_expr = filter_expressions[0]
                    for expr in filter_expressions[1:]:
                        filter_expr = filter_expr & expr
                    scan_kwargs['FilterExpression'] = filter_expr
                
                response = followup_table.scan(**scan_kwargs)
        else:
            # No filters - scan all
            response = followup_table.scan(**scan_kwargs)
        
        items = response.get('Items', [])
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        logger.info(f"Retrieved {len(items)} follow-ups")
        
        return {
            'items': items,
            'lastEvaluatedKey': last_evaluated_key
        }
    
    except Exception as e:
        logger.error(f"Failed to query follow-ups: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


def get_followup_by_id(followup_id, timestamp=None):
    """
    Get a specific follow-up by ID.
    If timestamp is provided, gets that specific version.
    Otherwise, queries to get the latest version.
    
    Args:
        followup_id: Follow-up identifier
        timestamp: Optional timestamp (sort key)
    
    Returns:
        dict: Follow-up object or None if not found
    """
    logger.info(f"Getting follow-up: {followup_id}, timestamp: {timestamp}")
    
    try:
        if timestamp:
            # Get specific version with both keys
            response = followup_table.get_item(
                Key={
                    'id': followup_id,
                    'timestamp': timestamp
                }
            )
            item = response.get('Item')
        else:
            # Query to get latest version (most recent timestamp)
            response = followup_table.query(
                KeyConditionExpression=Key('id').eq(followup_id),
                ScanIndexForward=False,  # Sort descending (newest first)
                Limit=1
            )
            items = response.get('Items', [])
            item = items[0] if items else None
        
        if item:
            logger.info(f"Found follow-up {followup_id}")
        else:
            logger.warning(f"Follow-up {followup_id} not found")
        
        return item
    
    except Exception as e:
        logger.error(f"Failed to get follow-up: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


def update_followup(followup_id, timestamp, updates):
    """
    Update a follow-up's status, assignment, or notes.
    
    Args:
        followup_id: Follow-up identifier
        timestamp: Timestamp of the follow-up (sort key)
        updates: Dictionary of fields to update (status, assignedTo, notes)
    
    Returns:
        dict: Updated follow-up item
    """
    logger.info(f"Updating follow-up {followup_id} with updates: {updates}")
    
    try:
        # Validate status if provided
        if 'status' in updates and updates['status'] not in constants.VALID_STATUSES:
            raise ValueError(f"Invalid status value: {updates['status']}")
        
        # Build update expression
        update_parts = []
        expression_values = {
            ':updated': datetime.utcnow().isoformat()
        }
        expression_names = {}
        
        # Always update the updatedAt timestamp
        update_parts.append('updatedAt = :updated')
        
        # Add status update if provided
        if 'status' in updates:
            update_parts.append('#status = :status')
            expression_values[':status'] = updates['status']
            expression_names['#status'] = 'status'  # 'status' is a reserved word
        
        # Add assignedTo update if provided
        if 'assignedTo' in updates:
            update_parts.append('assignedTo = :assignedTo')
            expression_values[':assignedTo'] = updates['assignedTo']
        
        # Add notes update if provided
        if 'notes' in updates:
            update_parts.append('notes = :notes')
            expression_values[':notes'] = updates['notes']
        
        # Construct the full update expression
        update_expression = 'SET ' + ', '.join(update_parts)
        
        # Prepare update_item parameters
        update_params = {
            'Key': {
                'id': followup_id,
                'timestamp': timestamp
            },
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        # Add ExpressionAttributeNames only if needed
        if expression_names:
            update_params['ExpressionAttributeNames'] = expression_names
        
        response = followup_table.update_item(**update_params)
        
        updated_item = response.get('Attributes')
        logger.info(f"Follow-up updated successfully")
        
        return updated_item
    
    except Exception as e:
        logger.error(f"Failed to update follow-up: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_filters(query_params, filter_type='conversation'):
    """
    Parse query string parameters into filter dictionary.
    
    Args:
        query_params: Dictionary of query string parameters
        filter_type: 'conversation' or 'followup'
    
    Returns:
        dict: Validated filter dictionary
    """
    logger.info(f"Parsing filters for {filter_type}: {query_params}")
    
    filters = {}
    
    if filter_type == 'conversation':
        # Parse conversation filters
        if 'flag' in query_params:
            flag = query_params['flag']
            if flag not in constants.VALID_FLAGS:
                raise ValueError(f"Invalid flag value: {flag}. Must be one of: {', '.join(constants.VALID_FLAGS)}")
            filters['flag'] = flag
        
        if 'userId' in query_params:
            filters['userId'] = query_params['userId']
        
        if 'county' in query_params:
            filters['county'] = query_params['county']
    
    elif filter_type == 'followup':
        # Parse follow-up filters
        if 'status' in query_params:
            status = query_params['status']
            if status not in constants.VALID_STATUSES:
                raise ValueError(f"Invalid status value: {status}. Must be one of: {', '.join(constants.VALID_STATUSES)}")
            filters['status'] = status
        
        if 'priority' in query_params:
            priority = query_params['priority']
            if priority not in constants.VALID_PRIORITIES:
                raise ValueError(f"Invalid priority value: {priority}. Must be one of: {', '.join(constants.VALID_PRIORITIES)}")
            filters['priority'] = priority
        
        if 'requestType' in query_params:
            request_type = query_params['requestType']
            if request_type not in constants.VALID_REQUEST_TYPES:
                raise ValueError(f"Invalid requestType value: {request_type}. Must be one of: {', '.join(constants.VALID_REQUEST_TYPES)}")
            filters['requestType'] = request_type
        
        if 'assignedTo' in query_params:
            filters['assignedTo'] = query_params['assignedTo']
    
    logger.info(f"Parsed filters: {filters}")
    return filters


def build_response(status_code, body, error=False):
    """
    Build a properly formatted HTTP response for API Gateway.
    
    Args:
        status_code: HTTP status code
        body: Response body (will be JSON serialized)
        error: Whether this is an error response
    
    Returns:
        dict: Formatted HTTP response
    """
    import json
    
    # Convert Decimal objects to JSON-serializable types
    body = decimal_to_number(body)
    
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,PUT,OPTIONS'
        },
        'body': json.dumps(body)
    }
    
    if error:
        logger.warning(f"Error response: {status_code} - {body}")
    
    return response