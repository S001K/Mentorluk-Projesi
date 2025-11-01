from memory import add_memory, get_raw_chat_history
from agents import summarization_chain
from utils import logger

def trigger_memory_summarization(session_id: str, user_id: str, persona: str):
    """
    Runs in the background AFTER the response is sent.
    Fetches *only the last two messages*, generates facts,
    and saves them to PGVector.
    """
    try:
        logger.info(f"[Background Task] Starting memory summarization for user '{user_id}', session '{session_id}'...")
        raw_history = get_raw_chat_history(session_id)

        if not raw_history or len(raw_history) < 2:
            logger.info("[Background Task] Not enough chat history to summarize (need at least 2 messages).")
            return

        recent_history = raw_history[-2:]
        extracted_facts_str = summarization_chain.invoke(recent_history)

        if not extracted_facts_str or extracted_facts_str.strip().lower() == "none":
            logger.info("[Background Task] No new facts extracted from conversation.")
            return

        facts = [fact.strip() for fact in extracted_facts_str.split("\n") if fact.strip()]
        logger.info(f"[Background Task] Extracted {len(facts)} new facts. Saving to PGVector...")

        for fact in facts:
            if fact:
                add_memory(text=fact, user_id=user_id, persona_id=persona)

        logger.info(f"[Background Task] Memory summarization finished for user '{user_id}'.")

    except Exception as e:
        logger.error(f"[Background Task] Failed during memory summarization: {e}", exc_info=True)