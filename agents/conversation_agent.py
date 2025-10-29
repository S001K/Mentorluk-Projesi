import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnableLambda

from config import MEMORY_WINDOW_SIZE, PERSONA_PROMPTS
from memory.short_term import get_session_history
from llm import llm as model

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
    # 1. Find the filename
    # Use "alex" as a safe default if the persona is not found
    prompt_filename = PERSONA_PROMPTS.get(persona_name, PERSONA_PROMPTS["alex"])

    # 2. Şablona aktarılacak değişkenleri tanımla
    template_variables = {
        "user_name": "Sinan"
    }

    # 3. Seçilen sistem prompt'unu yükle ve render et
    try:
        template = jinja_env.get_template(prompt_filename)
        return template.render(template_variables)
    except Exception as e:
        print(f"Uyarı: Jinja şablonu '{prompt_filename}' yüklenemedi. Hata: {e}")
        raise e

# --- NEW: Chain Helper Functions ---
def add_system_prompt(data):
    """
    RunnableLambda function to load and add the
    'system_prompt' to the data dictionary.
    """
    # Get the persona from the input
    persona = data.get("persona", "alex")  # Default to 'alex'

    # Load the prompt and add it to the dictionary
    data["system_prompt"] = load_persona_prompt(persona)
    return data


def trim_history(data):
    """
    (This is your existing function, unchanged)
    """
    if "history" in data:
        data["history"] = data["history"][-MEMORY_WINDOW_SIZE:]
    return data


# --- 1. Çekirdek Zinciri Tanımla (Prompt + Model) ---

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# --- 3. Zinciri birleştir (REBUILT) ---

chain = (
        RunnableLambda(add_system_prompt)  # Input -> adds 'system_prompt'
        | RunnableLambda(trim_history)  # Input -> trims 'history'
        | prompt  # Input -> formatted prompt
        | model  # Prompt -> AIMessage
)

# --- 4. Zinciri Hafıza ile Sar (REBUILT) ---
conversation_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
    # This tells the memory wrapper to allow the 'persona' key
    # to be passed through to the 'chain' defined above.
    chain_input_passthrough_keys=["persona"],
)