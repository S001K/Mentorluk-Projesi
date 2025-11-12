from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda
from langchain_core.messages import BaseMessage

from config import SETTINGS
from config import llm as model
from memory.short_term import get_session_history
from utils import PersonaNotFoundException, TemplateLoadException, logger

memory_window_size = SETTINGS.MEMORY_WINDOW_SIZE
persona_prompts = SETTINGS.PERSONA_PROMPTS

# --- Jinja Setup ---
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "prompt_templates"
template_loader = FileSystemLoader(searchpath=TEMPLATES_DIR)
jinja_env = Environment(
    loader=template_loader,
    autoescape=select_autoescape(['html', 'xml'])
)

# --- Dynamic Prompt Loading Function ---
def load_persona_prompt(persona_name: str) -> str:
    """
    Loads and renders the system prompt for the given persona.
    """
    prompt_filename = persona_prompts.get(persona_name)

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


# --- Chain Helper Functions ---

def add_system_prompt(data):
    persona = data.get("persona", "alex")
    data["system_prompt"] = load_persona_prompt(persona)
    return data


def trim_history(data):
    if "history" in data:
        data["history"] = data["history"][-memory_window_size:]
    return data


# --- NEW: Logging Functions for the Chain ---

def log_prompt_to_model(prompt_value: PromptValue) -> PromptValue:
    """
    RunnableLambda function to log the fully formatted prompt
    (as a list of messages) before it is sent to the LLM.
    """
    messages = prompt_value.to_messages()
    logger.debug(f"Sending prompt to Ollama with {len(messages)} messages:")
    for msg in messages:
        logger.debug(f"  [{msg.type.upper()}] {msg.content!r}...")
    return prompt_value


def log_final_response(ai_message: BaseMessage) -> BaseMessage:
    """
    RunnableLambda function to log the final, complete AI response
    after all streaming chunks are combined.
    """
    logger.debug(f"Received final response from Ollama: {ai_message.content!r}")
    return ai_message


# --- 1. Core Chain Definition ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# --- 2. Assemble the Chain (UPDATED) ---
# We insert our logging functions into the chain.
chain = (
        RunnableLambda(add_system_prompt)
        | RunnableLambda(trim_history)
        | prompt
        | RunnableLambda(log_prompt_to_model)
        | model
        | RunnableLambda(log_final_response)
)

# --- 3. Wrap the Chain with Memory ---
conversation_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
    chain_input_passthrough_keys=["persona"],
)