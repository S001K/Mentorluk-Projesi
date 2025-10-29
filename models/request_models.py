from pydantic import BaseModel
from config import DEFAULT_SESSION_ID

class ChatRequest(BaseModel):
    """
    Pydantic model for the chat request body.
    """
    input: str
    session_id: str = DEFAULT_SESSION_ID
    # The client can send "miki", "alex", or "kaito".
    persona: str

