import json
import logging
import traceback
from utilities import converse_with_model_no_guardrails
from prompts import followup_prompt
import dynamodb_utils
import constants

logger = logging.getLogger(__name__)

# Model configuration for follow-up detection
FOLLOWUP_MODEL_ID = "us.amazon.nova-pro-v1:0"  # Same model as main chatbot
FOLLOWUP_TEMPERATURE = 0.1  # Lower temperature for more consistent classification


def analyze_for_followup(user_message, user_info, conversation_id):
    """
    Analyze a user message to determine if follow-up is needed.
    
    Args:
        user_message: The user's latest message text
        user_info: User information dictionary
        conversation_id: ID of the conversation being analyzed
    
    Returns:
        dict: Follow-up analysis result with keys:
            - needs_followup (bool)
            - request_type (str): 'crisis', 'normal', or 'none'
            - priority (str): 'urgent' or 'normal'
            - conversation_flag (str): 'crisis', 'followup', or 'none'
            - reasoning (str)
            - preferred_contact (str or None)
    """
    logger.info(f"Analyzing message for follow-up: conversation {conversation_id}")
    
    try:
        # Build the prompt
        formatted_prompt = followup_prompt.prompt.format(
            userInfo=json.dumps(user_info, indent=2),
            userMessage=user_message
        )
        
        # Create message for the model
        messages = [{
            "role": "user",
            "content": [{"text": formatted_prompt}]
        }]
        
        # Call the model WITHOUT guardrails (non-streaming)
        response = converse_with_model_no_guardrails(
            modelId=FOLLOWUP_MODEL_ID,
            chatHistory=messages,
            config={"temperature": FOLLOWUP_TEMPERATURE},
            system=None,  # Prompt is in the user message
            streaming=False
        )
        
        # Extract the response text
        response_text = response["output"]["message"]["content"][0]["text"]
        logger.info(f"Follow-up detection response: {response_text[:200]}...")
        
        # Parse and validate the JSON
        followup_result = parse_followup_json(response_text)
        
        logger.info(f"Follow-up analysis complete: {followup_result}")
        return followup_result
        
    except Exception as e:
        logger.error(f"Follow-up analysis failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        # Return safe default (no follow-up) on error
        return {
            "needs_followup": False,
            "request_type": "none",
            "priority": "normal",
            "conversation_flag": "none",
            "reasoning": "Error during analysis - defaulting to no follow-up",
            "preferred_contact": None
        }


def parse_followup_json(response_text):
    """
    Parse and validate the JSON response from follow-up detection.
    
    Args:
        response_text: Raw text response from the model
    
    Returns:
        dict: Validated follow-up result
    """
    logger.info("Parsing follow-up JSON response")
    
    try:
        # Try to parse JSON
        result = json.loads(response_text)
        
        # Validate required fields
        required_fields = ["needs_followup", "request_type", "priority", "conversation_flag"]
        for field in required_fields:
            if field not in result:
                logger.warning(f"Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")
        
        # Validate field values
        valid_request_types = ["crisis", "normal", "none"]
        valid_priorities = ["urgent", "normal"]
        valid_flags = ["crisis", "followup", "none"]
        
        if result["request_type"] not in valid_request_types:
            logger.warning(f"Invalid request_type: {result['request_type']}")
            result["request_type"] = "none"
        
        if result["priority"] not in valid_priorities:
            logger.warning(f"Invalid priority: {result['priority']}")
            result["priority"] = "normal"
        
        if result["conversation_flag"] not in valid_flags:
            logger.warning(f"Invalid conversation_flag: {result['conversation_flag']}")
            result["conversation_flag"] = "none"
        
        # Ensure needs_followup is boolean
        result["needs_followup"] = bool(result["needs_followup"])
        
        # Validate logical consistency
        if result["request_type"] == "crisis":
            if result["priority"] != "urgent" or result["conversation_flag"] != "crisis":
                logger.warning("Fixing crisis inconsistency")
                result["priority"] = "urgent"
                result["conversation_flag"] = "crisis"
                result["needs_followup"] = True
        
        elif result["request_type"] == "normal":
            if result["conversation_flag"] != "followup":
                logger.warning("Fixing normal follow-up inconsistency")
                result["conversation_flag"] = "followup"
                result["needs_followup"] = True
        
        elif result["request_type"] == "none":
            result["needs_followup"] = False
            result["conversation_flag"] = "none"
        
        logger.info("JSON parsed and validated successfully")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.debug(f"Response text: {response_text}")
        # Return safe default
        return {
            "needs_followup": False,
            "request_type": "none",
            "priority": "normal",
            "conversation_flag": "none",
            "reasoning": "JSON parsing error - defaulting to no follow-up",
            "preferred_contact": None
        }
    
    except Exception as e:
        logger.error(f"JSON validation error: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        # Return safe default
        return {
            "needs_followup": False,
            "request_type": "none",
            "priority": "normal",
            "conversation_flag": "none",
            "reasoning": "Validation error - defaulting to no follow-up",
            "preferred_contact": None
        }


def process_followup_result(followup_result, conversation_id, timestamp, user_info):
    """
    Process the follow-up detection result and update DynamoDB accordingly.
    
    Args:
        followup_result: Result from analyze_for_followup()
        conversation_id: ID of the conversation
        timestamp: Timestamp of the conversation
        user_info: User information dictionary
    """
    logger.info(f"Processing follow-up result for conversation {conversation_id}")
    
    try:
        # Always update conversation flag if it's not 'none'
        if followup_result['conversation_flag'] != 'none':
            logger.info(f"Updating conversation flag to: {followup_result['conversation_flag']}")
            dynamodb_utils.update_conversation_flag(
                conversation_id=conversation_id,
                timestamp=timestamp,
                new_flag=followup_result['conversation_flag']
            )
        
        # Only create follow-up record if needed AND contact info exists
        if followup_result['needs_followup']:
            email = user_info.get('email')
            phone = user_info.get('phone')
            
            if email or phone:
                logger.info(f"Creating follow-up record for conversation {conversation_id}")
                
                # Determine preferred contact
                preferred_contact = followup_result.get('preferred_contact')
                if not preferred_contact:
                    # Default logic if LLM didn't specify
                    if email and not phone:
                        preferred_contact = 'email'
                    elif phone and not email:
                        preferred_contact = 'phone'
                    elif email:  # Both exist, prefer email
                        preferred_contact = 'email'
                
                # Extract user details
                user_id = dynamodb_utils.extract_user_id(user_info)
                county = dynamodb_utils.extract_county(user_info)
                
                # Generate conversation summary (use reasoning as summary)
                conversation_summary = followup_result.get('reasoning', 'Follow-up requested')
                
                # Create follow-up record
                dynamodb_utils.save_followup(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    county=county,
                    email=email,
                    phone=phone,
                    preferred_contact=preferred_contact,
                    conversation_summary=conversation_summary,
                    request_type=followup_result['request_type'],
                    priority=followup_result['priority'],
                    status='new'
                )
                
                logger.info(f"Follow-up record created successfully")
            else:
                logger.warning(
                    f"Follow-up needed for conversation {conversation_id} "
                    f"but no contact info provided (email: {email}, phone: {phone})"
                )
        else:
            logger.info(f"No follow-up needed for conversation {conversation_id}")
    
    except Exception as e:
        logger.error(f"Failed to process follow-up result: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        # Don't raise - we don't want follow-up processing errors to break the conversation