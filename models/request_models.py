# models/request_models.py
from enum import Enum

from pydantic import BaseModel

from config import SETTINGS


class Persona(str, Enum):
    MIKI = "miki"
    ALEX = "alex"
    KAITO = "kaito"


class ChatRequest(BaseModel):
    """
    Pydantic model for the chat request body.
    """
    input: str
    session_id: str = SETTINGS.DEFAULT_SESSION_ID
    # The client can send "miki", "alex", or "kaito".
    persona: Persona
