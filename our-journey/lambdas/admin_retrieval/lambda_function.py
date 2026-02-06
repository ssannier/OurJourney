import json
import logging
import traceback
import constants  # This configures logging
from utilities import (
    query_conversations,
    get_conversation_by_id,
    update_conversation_flag,
    query_followups,
    get_followup_by_id,
    update_followup,
    build_response,
    parse_filters
)

logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    """
    AWS Lambda handler for admin retrieval API.
    Routes requests to appropriate handlers based on HTTP method and path.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract request details
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        
        logger.info(f"Method: {http_method}, Path: {path}")
        
        # Route to appropriate handler
        if path == '/conversations':
            if http_method == 'GET':
                return handle_list_conversations(query_params)
            else:
                return build_response(405, {"error": "Method not allowed"}, error=True)
        
        elif path.startswith('/conversations/'):
            conversation_id = path_parameters.get('id')
            if not conversation_id:
                return build_response(400, {"error": "Missing conversation ID"}, error=True)
            
            if http_method == 'GET':
                return handle_get_conversation(conversation_id)
            elif http_method == 'PUT':
                body = json.loads(event.get('body', '{}'))
                return handle_update_conversation(conversation_id, body)
            else:
                return build_response(405, {"error": "Method not allowed"}, error=True)
        
        elif path == '/followups':
            if http_method == 'GET':
                return handle_list_followups(query_params)
            else:
                return build_response(405, {"error": "Method not allowed"}, error=True)
        
        elif path.startswith('/followups/'):
            followup_id = path_parameters.get('id')
            if not followup_id:
                return build_response(400, {"error": "Missing followup ID"}, error=True)
            
            if http_method == 'GET':
                return handle_get_followup(followup_id)
            elif http_method == 'PUT':
                body = json.loads(event.get('body', '{}'))
                return handle_update_followup(followup_id, body)
            else:
                return build_response(405, {"error": "Method not allowed"}, error=True)
        
        else:
            return build_response(404, {"error": "Resource not found"}, error=True)
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return build_response(400, {"error": "Invalid JSON in request body"}, error=True)
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Internal server error"}, error=True)


# ============================================================================
# CONVERSATION HANDLERS
# ============================================================================

def handle_list_conversations(query_params):
    """
    Handle GET /conversations
    List conversations with optional filtering and pagination.
    
    Query parameters:
    - flag: Filter by flag status (none/crisis/followup/resolved)
    - userId: Filter by user ID
    - county: Filter by county
    - limit: Number of items per page (default 50, max 100)
    - startKey: Pagination token from previous response
    """
    logger.info("Handling list conversations request")
    
    try:
        # Parse filters
        filters = parse_filters(query_params, filter_type='conversation')
        
        # Parse pagination parameters
        limit = int(query_params.get('limit', constants.DEFAULT_LIMIT))
        if limit < 1 or limit > constants.MAX_LIMIT:
            return build_response(400, {
                "error": "Invalid limit",
                "message": f"Limit must be between 1 and {constants.MAX_LIMIT}"
            }, error=True)
        
        start_key = query_params.get('startKey')
        if start_key:
            try:
                start_key = json.loads(start_key)
            except json.JSONDecodeError:
                return build_response(400, {
                    "error": "Invalid startKey",
                    "message": "startKey must be valid JSON"
                }, error=True)
        
        # Query conversations
        result = query_conversations(
            filters=filters,
            limit=limit,
            start_key=start_key
        )
        
        # Format response
        response_body = {
            "items": result['items'],
            "count": len(result['items'])
        }
        
        if result.get('lastEvaluatedKey'):
            response_body['nextPageKey'] = json.dumps(result['lastEvaluatedKey'])
        
        logger.info(f"Returning {len(result['items'])} conversations")
        return build_response(200, response_body)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return build_response(400, {"error": str(e)}, error=True)
    
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Failed to list conversations"}, error=True)


def handle_get_conversation(conversation_id):
    """
    Handle GET /conversations/{id}
    Get a specific conversation by ID.
    """
    logger.info(f"Handling get conversation request: {conversation_id}")
    
    try:
        conversation = get_conversation_by_id(conversation_id)
        
        if not conversation:
            return build_response(404, {
                "error": "Conversation not found",
                "conversationId": conversation_id
            }, error=True)
        
        logger.info(f"Returning conversation {conversation_id}")
        return build_response(200, conversation)
    
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Failed to get conversation"}, error=True)


def handle_update_conversation(conversation_id, body):
    """
    Handle PUT /conversations/{id}
    Update a conversation's flag status.
    
    Body parameters:
    - flag: New flag value (none/crisis/followup/resolved)
    - timestamp: Timestamp of the conversation (required for update)
    """
    logger.info(f"Handling update conversation request: {conversation_id}")
    
    try:
        # Validate required fields
        new_flag = body.get('flag')
        timestamp = body.get('timestamp')
        
        if not new_flag:
            return build_response(400, {
                "error": "Missing required field",
                "message": "flag is required"
            }, error=True)
        
        if not timestamp:
            return build_response(400, {
                "error": "Missing required field",
                "message": "timestamp is required"
            }, error=True)
        
        # Validate flag value
        valid_flags = ['none', 'crisis', 'followup', 'resolved']
        if new_flag not in valid_flags:
            return build_response(400, {
                "error": "Invalid flag value",
                "message": f"Flag must be one of: {', '.join(valid_flags)}"
            }, error=True)
        
        # Update conversation
        updated = update_conversation_flag(
            conversation_id=conversation_id,
            timestamp=timestamp,
            new_flag=new_flag
        )
        
        logger.info(f"Updated conversation {conversation_id} flag to {new_flag}")
        return build_response(200, {
            "id": conversation_id,
            "timestamp": timestamp,
            "flag": new_flag,
            "message": "Conversation updated successfully"
        })
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return build_response(400, {"error": str(e)}, error=True)
    
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Failed to update conversation"}, error=True)


# ============================================================================
# FOLLOW-UP HANDLERS
# ============================================================================

def handle_list_followups(query_params):
    """
    Handle GET /followups
    List follow-ups with optional filtering and pagination.
    
    Query parameters:
    - status: Filter by status (new/in-progress/completed)
    - priority: Filter by priority (normal/urgent)
    - requestType: Filter by request type (normal/crisis)
    - limit: Number of items per page (default 50, max 100)
    - startKey: Pagination token from previous response
    """
    logger.info("Handling list follow-ups request")
    
    try:
        # Parse filters
        filters = parse_filters(query_params, filter_type='followup')
        
        # Parse pagination parameters
        limit = int(query_params.get('limit', constants.DEFAULT_LIMIT))
        if limit < 1 or limit > constants.MAX_LIMIT:
            return build_response(400, {
                "error": "Invalid limit",
                "message": f"Limit must be between 1 and {constants.MAX_LIMIT}"
            }, error=True)
        
        start_key = query_params.get('startKey')
        if start_key:
            try:
                start_key = json.loads(start_key)
            except json.JSONDecodeError:
                return build_response(400, {
                    "error": "Invalid startKey",
                    "message": "startKey must be valid JSON"
                }, error=True)
        
        # Query follow-ups
        result = query_followups(
            filters=filters,
            limit=limit,
            start_key=start_key
        )
        
        # Format response
        response_body = {
            "items": result['items'],
            "count": len(result['items'])
        }
        
        if result.get('lastEvaluatedKey'):
            response_body['nextPageKey'] = json.dumps(result['lastEvaluatedKey'])
        
        logger.info(f"Returning {len(result['items'])} follow-ups")
        return build_response(200, response_body)
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return build_response(400, {"error": str(e)}, error=True)
    
    except Exception as e:
        logger.error(f"Error listing follow-ups: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Failed to list follow-ups"}, error=True)


def handle_get_followup(followup_id):
    """
    Handle GET /followups/{id}
    Get a specific follow-up by ID.
    """
    logger.info(f"Handling get follow-up request: {followup_id}")
    
    try:
        followup = get_followup_by_id(followup_id)
        
        if not followup:
            return build_response(404, {
                "error": "Follow-up not found",
                "followupId": followup_id
            }, error=True)
        
        logger.info(f"Returning follow-up {followup_id}")
        return build_response(200, followup)
    
    except Exception as e:
        logger.error(f"Error getting follow-up: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Failed to get follow-up"}, error=True)


def handle_update_followup(followup_id, body):
    """
    Handle PUT /followups/{id}
    Update a follow-up's status, assignment, or notes.
    
    Body parameters:
    - timestamp: Timestamp of the follow-up (required)
    - status: New status (new/in-progress/completed) [optional]
    - assignedTo: Person assigned to handle follow-up [optional]
    - notes: Additional notes [optional]
    """
    logger.info(f"Handling update follow-up request: {followup_id}")
    
    try:
        # Validate required fields
        timestamp = body.get('timestamp')
        if not timestamp:
            return build_response(400, {
                "error": "Missing required field",
                "message": "timestamp is required"
            }, error=True)
        
        # Extract optional update fields
        updates = {}
        
        if 'status' in body:
            status = body['status']
            valid_statuses = ['new', 'in-progress', 'completed']
            if status not in valid_statuses:
                return build_response(400, {
                    "error": "Invalid status value",
                    "message": f"Status must be one of: {', '.join(valid_statuses)}"
                }, error=True)
            updates['status'] = status
        
        if 'assignedTo' in body:
            updates['assignedTo'] = body['assignedTo']
        
        if 'notes' in body:
            updates['notes'] = body['notes']
        
        if not updates:
            return build_response(400, {
                "error": "No updates provided",
                "message": "At least one of: status, assignedTo, or notes is required"
            }, error=True)
        
        # Update follow-up
        updated = update_followup(
            followup_id=followup_id,
            timestamp=timestamp,
            updates=updates
        )
        
        logger.info(f"Updated follow-up {followup_id}")
        return build_response(200, {
            "id": followup_id,
            "timestamp": timestamp,
            "updates": updates,
            "message": "Follow-up updated successfully"
        })
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return build_response(400, {"error": str(e)}, error=True)
    
    except Exception as e:
        logger.error(f"Error updating follow-up: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        return build_response(500, {"error": "Failed to update follow-up"}, error=True)