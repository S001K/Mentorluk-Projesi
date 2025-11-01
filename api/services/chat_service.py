from fastapi import BackgroundTasks
from agents import conversation_chain
from .background_service import trigger_memory_summarization
from utils import AppException, logger, filter_allowed_text


async def handle_chat_stream(
        session_id: str, user_id: str, user_input: str, persona: str,
        background_tasks: BackgroundTasks
):
    """
    Handles the streaming chat logic.
    Triggers a background task for summarization on success.
    """

    logger.info(
        f"New chat request received (STREAM) -> User: '{user_id}', Session: '{session_id}', Persona: '{persona}', Input: '{user_input[:50]}...'")

    config = {"configurable": {"session_id": session_id}}

    try:
        async for chunk in conversation_chain.astream(
                {
                    "input": user_input,
                    "persona": persona,
                    "user_id": user_id
                },
                config=config
        ):
            clean_chunk = filter_allowed_text(chunk.content)
            yield clean_chunk

        logger.info(f"Stream for session '{session_id}' completed successfully.")

        background_tasks.add_task(
            trigger_memory_summarization, session_id, user_id, persona
        )

    except AppException as e:
        logger.warning(f"Handled known application error for session '{session_id}': {e.message}")
        yield f"Error: {e.message}"

    except Exception as e:
        logger.error(f"An unexpected error occurred for session '{session_id}'!", exc_info=True)
        yield "An unexpected error occurred. Please try again."


async def handle_chat_invoke(
        session_id: str, user_id: str, user_input: str, persona: str,
        background_tasks: BackgroundTasks
) -> str:
    """
    Handles the non-streaming (invoke) chat logic.
    Triggers a background task for summarization on success.
    """

    logger.info(
        f"New chat request received (INVOKE) -> User: '{user_id}', Session: '{session_id}', Persona: '{persona}', Input: '{user_input[:50]}...'")

    config = {"configurable": {"session_id": session_id}}

    response_message = await conversation_chain.ainvoke(
        {
            "input": user_input,
            "persona": persona,
            "user_id": user_id
        },
        config=config
    )

    clean_response = filter_allowed_text(response_message.content)
    logger.info(f"Invoke for session '{session_id}' completed successfully.")

    background_tasks.add_task(
        trigger_memory_summarization, session_id, user_id, persona
    )

    return clean_response

