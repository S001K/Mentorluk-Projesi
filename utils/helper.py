import re
from typing import List
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage

from .template_manager import jinja_env
from .logging import logger
from .exceptions import PersonaNotFoundException, TemplateLoadException

from config import PERSONA_PROMPTS

# --- 1. Text Filtering (Mevcut Fonksiyon) ---

ALLOWED_CHARS_PATTERN = re.compile(
    r"[^a-zA-Z0-9\n\r .,?!';:\"\-()]",
    flags=re.UNICODE
)


def filter_allowed_text(text: str) -> str:
    """
    Bir metni, izin verilen karakterler (İngiliz alfabesi, rakamlar,
    yaygın noktalama işaretleri) dışında her şeyden temizler.
    """
    return ALLOWED_CHARS_PATTERN.sub(r'', text)


# --- 2. Persona Loading ---

def load_persona_prompt(persona_name: str) -> str:
    """
    Verilen persona için sistem prompt'unu yükler ve render eder.
    Hata durumunda loglama yapar ve hata fırlatır.
    """
    prompt_filename = PERSONA_PROMPTS.get(persona_name)

    if not prompt_filename:
        logger.error(f"PersonaNotFoundException: Persona '{persona_name}' not found in config.py.")
        raise PersonaNotFoundException(persona=persona_name)

    template_variables = {
        "user_name": "Sinan"
    }

    try:
        template = jinja_env.get_template(prompt_filename)
        rendered_prompt = template.render(template_variables)

        logger.info(f"Successfully loaded and rendered template '{prompt_filename}' for persona '{persona_name}'.")
        return rendered_prompt

    except Exception as e:
        logger.error(
            f"TemplateLoadException: Failed to load/render template '{prompt_filename}'.",
            exc_info=True
        )
        raise TemplateLoadException(filename=prompt_filename, error=e)


# --- 3. RAG Context Formatting ---

def format_retrieved_context(docs: List[Document]) -> str:
    """ Alınan dokümanları (hafızayı) tek bir metin bloğu olarak formatlar. """
    if not docs:
        logger.debug("No relevant context found in vector store.")
        return "No relevant context found."

    logger.debug(f"Retrieved {len(docs)} documents for context.")
    for i, doc in enumerate(docs):
        logger.debug(f"  Context {i + 1}: {doc.page_content[:100]!r}...")

    context_str = "\n".join(f"- {doc.page_content}" for doc in docs)
    return context_str


# --- 4. Summarizer History Formatting ---

def format_chat_history_for_summarizer(messages: List[BaseMessage]) -> str:
    """
    [HumanMessage, AIMessage] listesini 'Human: ...\nAI: ...\n'
    formatında tek bir metne dönüştürür.
    """
    history_str = ""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history_str += f"Human: {msg.content}\n"
        elif isinstance(msg, BaseMessage) and msg.type == "ai":
            history_str += f"AI: {msg.content}\n"
    return history_str