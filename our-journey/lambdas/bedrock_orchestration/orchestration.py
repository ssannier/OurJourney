import json
import logging
import traceback
from chatbot_config import get_prompt, get_config, get_id
from utilities import (
    converse_with_model,
    parse_and_send_response,    
    execute_knowledge_base_query,
    format_results_for_response,
)
import constants  # This configures logging

logger = logging.getLogger(__name__)


# Orchestrate the chat request processing
def orchestrate(event):
    """
    Main orchestration function for processing chat requests via WebSocket.
    
    """
    logger.info("Starting orchestration")
    
    # Extract WebSocket connection ID
    try:
        connectionId = event["requestContext"]["connectionId"]
        logger.info(f"Processing connection: {connectionId}")
    except KeyError:
        logger.error("Failed to extract connection ID")
        return None
    
    
    try:
        # Parse chat history & UserInfo
        chatHistory = json.loads(event["body"])["messages"]
        userInfo = json.loads(event["body"])["userInfo"]

        logger.info(f"Parsed {len(chatHistory)} messages")

        response = respond_to_query(chatHistory=chatHistory, userInfo=userInfo)
        parse_and_send_response(response, connectionId)
        logger.info("Answer processed successfully")
              
    except Exception as e:
        logger.error(f"Orchestration failed: {str(e)}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        if connectionId:
            parse_and_send_response("An unexpected error occurred. Please try again later.", 
                                  connectionId, classic=True, pure=True)
    
    logger.info("Orchestration completed")
    return None


# Respond to the user's query by orchestrating multiple stages.
def respond_to_query(chatHistory, userInfo):
    """
    Orchestrate the multi-stage pipeline to respond to  queries.
    """
    logger.info("Starting SQL query pipeline")
    
    try:

        
        specific_question = chatHistory[-1]['content'][-1].get('text', '') if chatHistory[-1].get('content') else ''

        # Stage 1: get answers from the database
        logger.info("Retrieving answers from the database")
        results = retrieve_answers_from_database(
            question=specific_question, 
            userInfo=userInfo
        )

        # Check if results are empty
        if not results:
            logger.warning("No results found for the specific question")
            results = "No results found for your query."

        # Format results for response
        results = format_results_for_response(specific_question, results)



        # Stage 3: Generate final response
        logger.info("Generating final response")
        final_response = get_final_response(
            chatHistory=chatHistory, 
            results=results,
            userInfo=userInfo
        )
        
        logger.info("pipeline completed")
        return final_response
        
    except Exception as e:
        logger.error(f"SQL pipeline failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


# Retrieve final response based on query results.
def get_final_response(chatHistory, results, userInfo):
    """
    Convert  query results into natural language response.
    Synthesizes data into conversational format that answers the user's question.
    """
    logger.info("Generating final response")
    
    try:

        response = converse_with_model(
            get_id(),
            chatHistory,
            config=get_config(),
            system=get_prompt(results=results, userInfo=userInfo),
            streaming=True
        )
        
        logger.info("Final response generated")
        return response
        
    except Exception as e:
        logger.error(f"Final response generation failed: {e}")
        raise


def retrieve_answers_from_database(question, userInfo):
    """
    Retrieve answers from the database based on the specific question.
    This function executes the SQL queries and returns the results. - All inside bedrock knowledge bases
    """
    logger.info("Retrieving answers from the database")
    
    # Convert userInfo to readable text, handling missing fields
    user_context_parts = []
    
    if userInfo.get('county'):
        user_context_parts.append(f"located in {userInfo['county']}")
    
    if userInfo.get('releaseDate'):
        user_context_parts.append(f"release date is {userInfo['releaseDate']}")
    
    if userInfo.get('age18Plus') is not None:
        age_status = "over 18" if userInfo['age18Plus'] else "under 18"
        user_context_parts.append(age_status)
    
    if userInfo.get('gender'):
        user_context_parts.append(f"gender is {userInfo['gender']}")
    
    if userInfo.get('email'):
        user_context_parts.append(f"email is {userInfo['email']}")
    
    if userInfo.get('phone'):
        user_context_parts.append(f"phone is {userInfo['phone']}")
    
    # Combine parts into a sentence, or use empty string if no user info
    if user_context_parts:
        user_context = f"User context: {', '.join(user_context_parts)}."
        query = f"{user_context}\n\nQuestion: {question}"
    else:
        query = question
    
    try:
        # Send question to the knowledge base
        results = execute_knowledge_base_query(query)
        logger.info("Database query executed successfully")
        return results
    except Exception as e:
        logger.error(f"Database retrieval failed: {e}")
        raise