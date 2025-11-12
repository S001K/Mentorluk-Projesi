import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM Configuration ---
# Set the provider: "ollama" or "openrouter"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Set the model name based on the provider
# e.g., "gemma3:1b-it-qat" for ollama
# e.g., "meta-llama/llama-3.3-70b-instruct:free" for openrouter
LLM_MODEL = os.getenv("LLM_MODEL", "gemma3:1b-it-qat")

# --- OpenRouter Configuration ---
# This is only needed if LLM_PROVIDER is "openrouter"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Memory Configuration ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_SESSION_ID = "default_session"
MEMORY_WINDOW_SIZE = 10  # Number of messages to keep in the prompt

# --- Persona Configuration ---
# Maps the persona names to their actual template files
PERSONA_PROMPTS = {
    "miki": "conversation_agent_miki_system_prompt.j2",
    "alex": "conversation_agent_alex_system_prompt.j2",
    "kaito": "conversation_agent_kaito_system_prompt.j2",
}

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
