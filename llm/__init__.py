# llm/__init__.py

from .ollama_client import OllamaClient

# Optional: provide a convenient shortcut
ollama_client = OllamaClient()
llm = ollama_client.get_chat_model()

__all__ = ["OllamaClient", "ollama_client", "llm"]
