"""
LLM Loader

This module reads the environment configuration from config.py,
selects the correct LLM provider (Ollama or OpenRouter),
and initializes a single 'llm' instance for the application.
"""

from langchain_ollama.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from config import (
    LLM_PROVIDER,
    LLM_MODEL,
    OPENROUTER_API_KEY
)
from utils import logger

llm = None

if LLM_PROVIDER == "ollama":
    try:
        logger.info(f"Initializing LLM with provider: 'ollama', model: '{LLM_MODEL}'")
        llm = ChatOllama(model=LLM_MODEL)
    except Exception as e:
        logger.error(f"Failed to connect to Ollama. Is it running? Error: {e}")
        raise

elif LLM_PROVIDER == "openrouter":
    if not OPENROUTER_API_KEY:
        logger.error("LLM_PROVIDER is 'openrouter' but OPENROUTER_API_KEY is not set.")
        raise ValueError("OPENROUTER_API_KEY is missing.")

    try:
        logger.info(f"Initializing LLM with provider: 'openrouter', model: '{LLM_MODEL}'")
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            streaming=True,
        )
    except Exception as e:
        logger.error(f"Failed to connect to OpenRouter. Check API key and model name. Error: {e}")
        raise

else:
    logger.error(f"Invalid LLM_PROVIDER: '{LLM_PROVIDER}'. Must be 'ollama' or 'openrouter'.")
    raise ValueError(f"Invalid LLM_PROVIDER specified in config.")