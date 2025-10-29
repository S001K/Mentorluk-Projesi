from langchain_redis import RedisChatMessageHistory
from config import REDIS_URL

def get_session_history(session_id: str) -> RedisChatMessageHistory:
    """
    Returns a Redis-backed chat history object for the given session_id.
    """
    return RedisChatMessageHistory(
        session_id=session_id,
        redis_url=REDIS_URL,
        ttl=1800  # History expires after 30 minutes of inactivity
    )
