# config/llm.py
"""
LLM Loader

This module reads the environment configuration from config.settings,
selects the correct LLM provider (OpenRouter or Groq),
and initializes a single 'llm' instance for the application.
"""

from typing import Final

from langchain_openai import ChatOpenAI

from config import SETTINGS
from utils import logger


def build_chat_openai_client() -> ChatOpenAI:
    """
    Factory for the global ChatOpenAI client.
    Supports OpenRouter and Groq backends via OpenAI-compatible API.
    """
    llm_provider = SETTINGS.LLM_PROVIDER
    llm_model = SETTINGS.LLM_MODEL

    if llm_provider.value == "openrouter":
        if not SETTINGS.OPENROUTER_API_KEY:
            logger.error("LLM_PROVIDER is 'openrouter' but OPENROUTER_API_KEY is not set.")
            raise ValueError("OPENROUTER_API_KEY is missing.")

        try:
            logger.info(f"Initializing LLM with provider='openrouter', model='{llm_model}'")
            return ChatOpenAI(
                model=llm_model,
                api_key=SETTINGS.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                streaming=True,
            )
        except Exception as e:
            logger.error("Failed to connect to OpenRouter.", exc_info=True)
            raise

    if llm_provider.value == "groq":
        if not SETTINGS.GROQ_API_KEY:
            logger.error("LLM_PROVIDER is 'groq' but GROQ_API_KEY is not set.")
            raise ValueError("GROQ_API_KEY is missing.")

        try:
            logger.info(f"Initializing LLM with provider='groq', model='{llm_model}'")
            return ChatOpenAI(
                model=llm_model,
                api_key=SETTINGS.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
                streaming=True,
            )
        except Exception as e:
            logger.error("Failed to connect to Groq.", exc_info=True)
            raise

    logger.error(f"Invalid LLM_PROVIDER: '{llm_provider}'. Must be 'openrouter' or 'groq'.")
    raise ValueError("Invalid LLM_PROVIDER specified in config.")


# Global, reusable client instance:
llm: Final[ChatOpenAI] = build_chat_openai_client()
