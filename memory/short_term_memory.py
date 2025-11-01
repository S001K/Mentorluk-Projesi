from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import List
from config import REDIS_URL
from utils import logger


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    Returns a Redis-backed chat history object for the given session_id.
    Used by the main conversation chain (RunnableWithMessageHistory).
    """
    return RedisChatMessageHistory(session_id, url=REDIS_URL, ttl=1800)

def get_raw_chat_history(session_id: str) -> List[BaseMessage]:
    """
    Fetches the raw list of messages from Redis for a given session_id.
    Used by the summarization background task.
    """
    try:
        history = RedisChatMessageHistory(session_id, url=REDIS_URL)
        return history.messages
    except Exception as e:
        logger.warning(f"Could not fetch raw chat history for session '{session_id}'. Error: {e}")
        return []