"""
LLM Loader

This module reads the environment configuration from config.py,
selects the correct LLM provider (OpenRouter, or Groq),
and initializes a single 'llm' instance for the application.
"""

from langchain_openai import ChatOpenAI
from config import SETTINGS
from utils import logger

llm = None
llm_provider = SETTINGS.LLM_PROVIDER
llm_model = SETTINGS.LLM_MODEL
openrouter_api_key = SETTINGS.OPENROUTER_API_KEY
groq_api_key = SETTINGS.GROQ_API_KEY


if llm_provider == "openrouter":
    if not openrouter_api_key:
        logger.error("LLM_PROVIDER is 'openrouter' but OPENROUTER_API_KEY is not set.")
        raise ValueError("OPENROUTER_API_KEY is missing.")

    try:
        logger.info(f"Initializing LLM with provider: 'openrouter', model: '{llm_model}'")
        llm = ChatOpenAI(
            model=llm_model,
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            streaming=True,
        )
    except Exception as e:
        logger.error(f"Failed to connect to OpenRouter. Check API key and model name. Error: {e}")
        raise

elif llm_provider == "groq":
    if not groq_api_key:
        logger.error("LLM_PROVIDER is 'groq' but GROQ_API_KEY is not set.")
        raise ValueError("GROQ_API_KEY is missing.")

    try:
        logger.info(f"Initializing LLM with provider: 'groq', model: '{llm_model}'")
        llm = ChatOpenAI(
            model=llm_model,
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            streaming=True,
        )
    except Exception as e:
        logger.error(f"Failed to connect to Groq. Check API key and model name. Error: {e}")
        raise

else:
    logger.error(f"Invalid LLM_PROVIDER: '{llm_provider}'. Must be 'openrouter', or 'groq'.")
    raise ValueError(f"Invalid LLM_PROVIDER specified in config.")