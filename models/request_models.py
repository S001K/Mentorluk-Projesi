from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    Pydantic model for the chat request.
    """
    input: str
    session_id: str
    user_id: str
    persona: str

class MemoryRequest(BaseModel):
    """
    Pydantic model for adding a new memory.
    """
    text: str
    user_id: str
    persona: str