# config/__init__.py
"""
This file exposes a single, cached instance of Settings (`SETTINGS`)
so other modules can import configuration safely and consistently:
    from config import SETTINGS
"""

from .settings import get_settings, SETTINGS, Settings, LLMProvider
from .llm_config import llm

__all__ = ["SETTINGS", "Settings", "get_settings", "LLMProvider", "llm"]
