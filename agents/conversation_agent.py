from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
# Gerekli importları (PromptValue dahil) doğru yerlerden al
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import (
    RunnableWithMessageHistory,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough
)
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document
from typing import List, Tuple  # Puanlama için Tuple importu

from config import MEMORY_WINDOW_SIZE, PERSONA_PROMPTS
# Hafıza paketinden güncellenmiş fonksiyonlarımızı alıyoruz
from memory import get_session_history, search_memories_with_score
from llm import llm

# Utils'ten gerekli yardımcıları ve ayarları alıyoruz
# (format_retrieved_context'i artık burada tanımlayacağımız için import etmiyoruz)
from utils import (
    logger,
    jinja_env,
    load_persona_prompt,
    PersonaNotFoundException,
    TemplateLoadException
)


# --- Dinamik Prompt Yükleme (Artık utils/helper.py'da) ---
# 'load_persona_prompt' fonksiyonu artık utils'ten geliyor


# --- Zincir Yardımcı Fonksiyonları ---

def add_system_prompt(data):
    """
    RunnableLambda fonksiyonu: Gelen 'persona'ya göre sistem prompt'unu yükler.
    """
    persona = data.get("persona", "alex")
    # 'utils'ten import edilen fonksiyonu çağır
    data["system_prompt"] = load_persona_prompt(persona)
    return data


def trim_history(data):
    """
    RunnableLambda fonksiyonu: 'history' listesini config'deki pencere boyutuna göre kırpar.
    """
    if "history" in data:
        data["history"] = data["history"][-MEMORY_WINDOW_SIZE:]
    return data


# --- RAG Yardımcı Fonksiyonları (Benzerlik Skoru için Güncellendi) ---

def format_retrieved_context(memory_results: List[Tuple[Document, float]]) -> str:
    """
    Alınan dokümanları VE PUANLARINI tek bir metin bloğu olarak formatlar.
    Ayrıca puanları loglar.
    """
    if not memory_results:
        logger.debug("No relevant context found in vector store.")
        return "No relevant context found."

    logger.debug(f"Retrieved {len(memory_results)} documents for context.")

    context_str_parts = []
    for i, (doc, score) in enumerate(memory_results):
        # PGVector (kosinüs mesafesi) 0.0'a yaklaştıkça benzerlik artar.
        # Bunu 100 üzerinden bir benzerlik yüzdesine çeviriyoruz.
        similarity_percent = (1.0 - score) * 100

        # Puanları ve metni logla
        logger.debug(
            f"  Context {i + 1} (Similarity: {similarity_percent:.2f}%): "
            f"{doc.page_content[:100]!r}..."
        )

        # Sadece metni (puanı değil) prompt'a ekle
        context_str_parts.append(f"- {doc.page_content}")

    context_str = "\n".join(context_str_parts)
    return context_str


def retrieve_context(input_data: dict):
    """
    Kullanıcıya özel hafızayı PUANLARIYLA birlikte dinamik olarak çeker.
    """
    user_id = input_data["user_id"]
    persona_id = input_data["persona"]
    input_text = input_data["input"]

    # Artık 'search_memories_with_score'u çağırıyoruz
    results_with_scores = search_memories_with_score(
        input_text=input_text,
        user_id=user_id,
        persona_id=persona_id
    )

    # Loglama 'format_retrieved_context' içinde yapılır
    return format_retrieved_context(results_with_scores)


# --- Loglama Fonksiyonları (Değişiklik yok) ---
def log_prompt_to_model(prompt_value: PromptValue) -> PromptValue:
    """
    LLM'e gönderilmeden hemen önce tam formatlanmış prompt'u loglar.
    """
    messages = prompt_value.to_messages()
    logger.debug(f"Sending prompt to LLM with {len(messages)} messages:")
    for msg in messages:
        logger.debug(f"  [{msg.type.upper()}] {msg.content[:120]!r}...")
    return prompt_value


def log_final_response(ai_message: BaseMessage) -> BaseMessage:
    """
    Tüm streaming bittikten sonra LLM'den gelen tam yanıtı loglar.
    """
    logger.debug(f"Received final response from LLM: {ai_message.content!r}")
    return ai_message


# --- Çekirdek Sohbet Zinciri (Değişiklik yok) ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}\n\n[Retrieved Context]\n{retrieved_context}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

chain_without_history = (
        RunnablePassthrough()
        .assign(
            system_prompt=(RunnableLambda(add_system_prompt) | (lambda x: x["system_prompt"])),
            retrieved_context=RunnableLambda(retrieve_context),
        )
        | RunnableLambda(trim_history)
        | prompt
        | RunnableLambda(log_prompt_to_model)
        | llm
        | RunnableLambda(log_final_response)
)

# --- Zinciri Hafıza ile Sar (Değişiklik yok) ---
conversation_chain = RunnableWithMessageHistory(
    chain_without_history,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
    chain_input_passthrough_keys=["persona", "user_id"],
)