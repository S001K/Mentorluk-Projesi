# memory/short_term.py
from langchain_community.chat_message_histories import RedisChatMessageHistory

from config import SETTINGS


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """
    Returns a Redis-backed chat history object for the given session_id.
    """
    return RedisChatMessageHistory(
        session_id=session_id,
        url=SETTINGS.REDIS_URL,
        ttl=SETTINGS.REDIS_TTL_SECONDS,
    )
