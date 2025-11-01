"""
Memory Management Service

This service handles the business logic for manually
interacting with the agent's memory.
"""
from memory import add_memory
from utils import AppException, logger

def handle_add_memory(text: str, user_id: str, persona: str):
    """
    Handles adding a new semantic memory for a specific user_id.
    (This function was moved from chat_service.py)
    """
    try:
        add_memory(text, user_id=user_id, persona_id=persona)
        logger.info(f"Successfully added new memory via API for user '{user_id}': '{text[:50]}...'")
    except Exception as e:
        logger.error(f"Failed to add memory via API: {e}", exc_info=True)
        raise AppException(message="Failed to write to vector store.", error=e)