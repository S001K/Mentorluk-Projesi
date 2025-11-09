
"""
Memory Package Interface

This __init__.py file exports all components for the memory layer
(both short-term Redis and long-term PGVector).
"""

# 1. From the short-term (Redis) session cache
from .short_term_memory import get_session_history, get_raw_chat_history

# --- GÜNCELLENDİ ---
# 2. From the long-term (PGVector) semantic memory
from .long_term_memory import search_memories_with_score, add_memory
# --- BİTTİ ---

# 3. Define the "public API" for this package
__all__ = [
    "get_session_history",
    "get_raw_chat_history",
    "search_memories_with_score",
    "add_memory"
]