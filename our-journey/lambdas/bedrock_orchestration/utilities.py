import boto3
from botocore.exceptions import ClientError
import json
import logging
import traceback
import constants  # This configures logging


logger = logging.getLogger(__name__)


# A function to initialize and return all AWS service clients
def get_clients():
    """Initialize and return all AWS service clients"""
    logger.info("Initializing AWS clients")
    
    try:
        apiGatewayURL = "https" + constants.API_GATEWAY_URL[3:] + "/prod"
        logger.info(f"API Gateway URL: {apiGatewayURL}")
        
        # Initialize AWS service clients
        gateway = boto3.client("apigatewaymanagementapi", endpoint_url=apiGatewayURL)
        bedrock = boto3.client('bedrock-runtime')
        s3_client = boto3.client('s3')
        agent = boto3.client('bedrock-agent-runtime')
        
        logger.info("AWS clients initialized successfully")
        return gateway, bedrock, s3_client, agent
        
    except Exception as e:
        logger.error(f"Failed to initialize AWS clients: {e}")
        raise

# Initialize AWS service clients
gateway, bedrock, s3_client, agent = get_clients()


# Function to send JSON data to client via WebSocket connection
def send_to_gateway(connectionId, json_data):
    """Send JSON data to client via WebSocket connection"""
    logger.info(f"Sending data to connection: {json_data}")
    
    try:
        gateway.post_to_connection(
            ConnectionId=connectionId, 
            Data=json.dumps(json_data)
        )
        logger.info("Data sent successfully")
        
    except ClientError as e:
        logger.error(f"Failed to send to gateway: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending to gateway: {e}")
        raise


# Function to converse with Bedrock AI model
def converse_with_model(modelId, chatHistory, config=None, system=None, streaming=False):
    """Get response from Bedrock AI model with optional streaming"""
    logger.info(f"Conversing with model: {modelId}, streaming: {streaming}")

    guardrails_streaming = constants.GUARDRAILS_CONFIG_STREAMING

    guardrails = constants.GUARDRAILS_CONFIG
    
    try:
        if streaming:
            response = bedrock.converse_stream(
                modelId=modelId,
                messages=chatHistory,
                inferenceConfig=config,
                system=system,
                guardrailConfig=guardrails_streaming
            )
        else:
            response = bedrock.converse(
                modelId=modelId,
                messages=chatHistory,
                inferenceConfig=config,
                system=system,
                guardrailConfig=guardrails
            )
        
        logger.info("Model conversation completed")
        return response
        
    except ClientError as e:
        logger.error(f"Bedrock client error: {e}")
        raise
    except Exception as e:
        logger.error(f"Model conversation failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


# Function to parse streaming response and send events to client 
# Classic is when the response is not streaming just one whole string message
# Pure is when the response is a string and not a dict from the model
# Info is an update for the frontend from before the final response is made (Info messages never stream, and are always sent as a single message)
def parse_and_send_response(response, connectionId, classic=None, pure=None, info=None):
    """Parse streaming response and send events to client in real-time"""
    logger.info("Parsing and sending response")
    
    # Initialize buffer for BREAK_TOKEN detection
    buffer = ""
    BREAK_TOKEN = "BREAK_TOKEN"
    
    try:

        # Handle info messages
        if info:
            json_data = {
                "type": "info",
                "data": response
            }
            send_to_gateway(connectionId, json_data)
            logger.info("Info message sent")
            return

        # Handle classic response (non-streaming)
        if classic:
            if pure:
                json_data = {
                    "message": response,
                }
            else:
                json_data = {
                    "message": response["output"]["message"]["content"][0]["text"],
                }
            send_to_gateway(connectionId, json_data)
            logger.info("Classic response sent")
            return
            
        # Handle streaming response
        stream = response.get('stream')
        if stream:
            event_count = 0
            for event in stream:
                event_count += 1
                
                # Handle content delta events (partial response chunks)
                if "contentBlockDelta" in event:
                    contentBlockDelta = event["contentBlockDelta"]
                    delta_text = contentBlockDelta.get("delta", {}).get("text", "")
                    
                    # Process BREAK_TOKEN detection
                    if buffer == "":
                        # Buffer is empty
                        if BREAK_TOKEN in delta_text:
                            # Full token found - split and send
                            parts = delta_text.split(BREAK_TOKEN, 1)
                            before_text = parts[0]
                            after_text = parts[1] if len(parts) > 1 else ""
                            
                            # Send text before token (if exists)
                            if before_text:
                                json_data = {
                                    "type": "contentBlockDelta",
                                    "data": {
                                        **contentBlockDelta,
                                        "delta": {
                                            **contentBlockDelta.get("delta", {}),
                                            "text": before_text
                                        }
                                    }
                                }
                                send_to_gateway(connectionId, json_data)
                            
                            # Send break token message
                            json_data = {
                                "type": "breakTokenType"
                            }
                            send_to_gateway(connectionId, json_data)
                            
                            # Send text after token (if exists)
                            if after_text:
                                json_data = {
                                    "type": "contentBlockDelta",
                                    "data": {
                                        **contentBlockDelta,
                                        "delta": {
                                            **contentBlockDelta.get("delta", {}),
                                            "text": after_text
                                        }
                                    }
                                }
                                send_to_gateway(connectionId, json_data)
                        else:
                            # Check if delta ends with partial BREAK_TOKEN
                            found_partial = False
                            for i in range(1, min(len(delta_text) + 1, len(BREAK_TOKEN) + 1)):
                                if delta_text.endswith(BREAK_TOKEN[:i]):
                                    # Found partial match at end
                                    prefix = delta_text[:-i]
                                    suffix = delta_text[-i:]
                                    
                                    # Send prefix if exists
                                    if prefix:
                                        json_data = {
                                            "type": "contentBlockDelta",
                                            "data": {
                                                **contentBlockDelta,
                                                "delta": {
                                                    **contentBlockDelta.get("delta", {}),
                                                    "text": prefix
                                                }
                                            }
                                        }
                                        send_to_gateway(connectionId, json_data)
                                    
                                    # Buffer the partial match
                                    buffer = suffix
                                    found_partial = True
                                    break
                            
                            if not found_partial:
                                # No partial match, send as normal
                                json_data = {
                                    "type": "contentBlockDelta",
                                    "data": contentBlockDelta
                                }
                                send_to_gateway(connectionId, json_data)
                    else:
                        # Buffer is not empty - try to complete the pattern
                        combined = buffer + delta_text
                        match_length = 0
                        
                        # Check character by character
                        for i, char in enumerate(delta_text):
                            if buffer + delta_text[:i+1] == BREAK_TOKEN[:len(buffer) + i + 1]:
                                match_length = i + 1
                                if buffer + delta_text[:i+1] == BREAK_TOKEN:
                                    # Pattern complete!
                                    # Send break token message
                                    json_data = {
                                        "type": "breakTokenType"
                                    }
                                    send_to_gateway(connectionId, json_data)
                                    
                                    # Clear buffer
                                    buffer = ""
                                    
                                    # Send remaining delta if exists
                                    remaining = delta_text[i+1:]
                                    if remaining:
                                        json_data = {
                                            "type": "contentBlockDelta",
                                            "data": {
                                                **contentBlockDelta,
                                                "delta": {
                                                    **contentBlockDelta.get("delta", {}),
                                                    "text": remaining
                                                }
                                            }
                                        }
                                        send_to_gateway(connectionId, json_data)
                                    break
                            else:
                                # Mismatch - false start
                                false_start_text = buffer + delta_text
                                json_data = {
                                    "type": "contentBlockDelta",
                                    "data": {
                                        **contentBlockDelta,
                                        "delta": {
                                            **contentBlockDelta.get("delta", {}),
                                            "text": false_start_text
                                        }
                                    }
                                }
                                send_to_gateway(connectionId, json_data)
                                
                                # Clear buffer
                                buffer = ""
                                break
                        else:
                            # Exhausted delta while matching - continue buffering
                            if match_length == len(delta_text):
                                buffer += delta_text
                                # Don't send anything, wait for next delta
                
                # Handle message start events
                elif "messageStart" in event:
                    json_data = {
                        "type": "messageStart",
                        "data": event["messageStart"]
                    }
                    send_to_gateway(connectionId, json_data)
                
                # Handle message completion events
                elif "messageStop" in event:
                    # If there's buffered content at message end, send it as false start
                    if buffer:
                        logger.warning(f"Incomplete BREAK_TOKEN at message end: {buffer}")
                        # Send buffered content as regular delta
                        json_data = {
                            "type": "contentBlockDelta",
                            "data": {
                                "delta": {
                                    "text": buffer
                                }
                            }
                        }
                        send_to_gateway(connectionId, json_data)
                        buffer = ""
                    
                    json_data = {
                        "type": "messageStop",
                        "data": event["messageStop"]
                    }
                    send_to_gateway(connectionId, json_data)
                
                # Log any unhandled event types
                elif "contentBlockStop" in event:
                    # skip
                    continue
                elif "metadata" in event:
                    # skip
                    continue
                else:
                    logger.warning(f"Unhandled event type: {event}")
            
            logger.info(f"Processed {event_count} streaming events")
            
    except Exception as e:
        logger.error(f"Response parsing failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


# Function to create a formatted conversation history for AI model input
def create_history(chatHistory):
    """Create a formatted conversation history for AI model input"""
    logger.info(f"Creating history from {len(chatHistory)} messages")
    
    try:
        history = ""
        for message in chatHistory:
            role = message["role"]
            content = message["content"][0]["text"]
            history += f"{role}: {content}\n\n"
        
        logger.info("Chat history formatted successfully")
        return history
        
    except KeyError as e:
        logger.error(f"Invalid message format in chat history: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create history: {e}")
        raise


# Function to execute a knowledge base query using Bedrock Agent Runtime
def execute_knowledge_base_query(question):
    try:
        # Set up the knowledge base ID and retrieval configuration
        knowledge_base_id = constants.KNOWLEDGE_BASE_ID
        query = {
            'text': question
        }
        
        retrieval_configuration = {
            'vectorSearchConfiguration': {
                'numberOfResults': int(constants.NUM_KB_RESULTS),
            }
        }
        
        # Retrieve from the Knowledge base
        logger.info(f"Retrieving from knowledge base with query: {query['text']}")
        kb_results = agent.retrieve(
            knowledgeBaseId=knowledge_base_id, 
            retrievalQuery=query, 
            retrievalConfiguration=retrieval_configuration
        )
        
        logger.info("Knowledge base retrieval successful")
        return kb_results
        
    except Exception as e:
        logger.error(f"Knowledge base retrieval failed: {e}")
        raise




def format_results_for_response(question, result):
    """Format a single question-result pair for final response"""
    logger.info("Formatting results for final response")
    try:
        # Format the single question-result pair
        final_response = f"Question asked was: {question}\nThe answer(s) found was: {result}"
        logger.info("Results formatted successfully")
        return final_response
    except Exception as e:
        logger.error(f"Failed to format results: {e}")
        raise

def extract_json_content(text):
    """
    Extracts content between the first '{' and last '}' in a string.
    
    Args:
        text (str): Input string containing JSON-like content
        
    Returns:
        str: Content between first '{' and last '}', or empty string if not found
    """
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    
    if first_brace != -1 and last_brace != -1 and first_brace <= last_brace:
        return text[first_brace:last_brace + 1]
    
    return ""
    