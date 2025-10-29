import os

# --- LLM Configuration ---
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:1b-it-qat")

# --- Memory Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_SESSION_ID = "default_session"
MEMORY_WINDOW_SIZE = 10  # Number of messages to keep in the prompt

# --- Persona Configuration ---
PERSONA_PROMPTS = {
    "miki": "conversation_agent_miki_system_prompt.j2",
    "alex": "conversation_agent_alex_system_prompt.j2",
    "kaito": "conversation_agent_kaito_system_prompt.j2",
}