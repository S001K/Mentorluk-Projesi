from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from llm import llm
from utils import (
    logger,
    jinja_env,
    format_chat_history_for_summarizer,
    TemplateLoadException
)


try:
    template = jinja_env.get_template("memory_agent_system_prompt.j2")
    SUMMARIZER_SYSTEM_PROMPT = template.render()
    logger.info("Summarizer agent prompt loaded successfully.")
except Exception as e:
    logger.error(f"FATAL: Failed to load summarizer prompt: {e}", exc_info=True)
    raise TemplateLoadException(filename="memory_agent_system_prompt", error=e)

logger.info(f"Summarization chain is using model: {llm.__class__.__name__}")
summarization_chain = (
    RunnableLambda(format_chat_history_for_summarizer)
    | ChatPromptTemplate.from_messages([
          ("system", SUMMARIZER_SYSTEM_PROMPT),
          ("human", "{input}")
      ])
    | llm
    | (lambda ai_msg: ai_msg.content)
)