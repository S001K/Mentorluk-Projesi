from pydantic import BaseModel
class ChatResponse(BaseModel):
    """
    Pydantic model for the non-streaming chat response.
    """
    response: str