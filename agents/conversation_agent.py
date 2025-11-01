from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import (
    RunnableWithMessageHistory,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough
)
from langchain_core.messages import BaseMessage

from config import MEMORY_WINDOW_SIZE
from memory import get_session_history, get_retriever_for_user
from llm import llm


from utils import (
    logger,
    jinja_env,
    load_persona_prompt,
    format_retrieved_context,
    PersonaNotFoundException,
    TemplateLoadException
)


# --- Zincir Yardımcı Fonksiyonları ---

def add_system_prompt(data):
    """
    RunnableLambda function to load and add the
    'system_prompt' to the data dictionary.
    """
    persona = data.get("persona")

    if not persona:
        raise PersonaNotFoundException

    data["system_prompt"] = load_persona_prompt(persona)
    return data


def trim_history(data):
    """
    Trims the 'history' list to MEMORY_WINDOW_SIZE.
    """
    if "history" in data:
        data["history"] = data["history"][-MEMORY_WINDOW_SIZE:]
    return data


def retrieve_context(input_data: dict):
    """
    Dynamically creates a user-specific retriever and fetches context.
    """
    user_id = input_data["user_id"]
    persona_id = input_data["persona"]

    retriever = get_retriever_for_user(user_id, persona_id)

    context_docs = retriever.invoke(input_data["input"])

    return format_retrieved_context(context_docs)


def log_prompt_to_model(prompt_value: PromptValue) -> PromptValue:
    """
    Logs the fully formatted prompt before it is sent to the LLM.
    """
    messages = prompt_value.to_messages()
    logger.debug(f"Sending prompt to LLM with {len(messages)} messages:")
    for msg in messages:
        logger.debug(f"  [{msg.type.upper()}] {msg.content[:120]!r}...")
    return prompt_value


def log_final_response(ai_message: BaseMessage) -> BaseMessage:
    """
    Logs the final, complete AI response after streaming.
    """
    logger.debug(f"Received final response from LLM: {ai_message.content!r}")
    return ai_message


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

conversation_chain = RunnableWithMessageHistory(
    chain_without_history,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
    chain_input_passthrough_keys=["persona", "user_id"],
)