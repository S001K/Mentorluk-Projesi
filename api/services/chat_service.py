from agents.conversation_agent import conversation_chain
from utils import AppException, logger, filter_allowed_text


async def handle_chat_stream(session_id: str, user_input: str, persona: str):
    """
    Handles the streaming chat logic by invoking the conversation chain.
    This is an async generator that yields response chunks.
    """

    logger.info(
        f"New chat request received (STREAM) -> Session: '{session_id}', Persona: '{persona}', Input: '{user_input}'")

    config = {"configurable": {"session_id": session_id}}

    try:
        # Run the chain
        async for chunk in conversation_chain.astream(
                {
                    "input": user_input,
                    "persona": persona
                },
                config=config
        ):
            clean_chunk = filter_allowed_text(chunk.content)
            yield clean_chunk

        logger.info(f"Stream for session '{session_id}' completed successfully.")

    except AppException as e:
        logger.warning(f"Handled known application error for session '{session_id}': {e.message}")
        yield f"Error: {e.message}"

    except Exception as e:
        logger.error(
            f"An unexpected error occurred for session '{session_id}'!",
            exc_info=True
        )
        yield "An unexpected error occurred. Please try again."


async def handle_chat_invoke(session_id: str, user_input: str, persona: str) -> str:
    """
    Handles the non-streaming chat logic by invoking the conversation chain.
    This function will propagate exceptions to be handled by the router.
    """

    logger.info(
        f"New chat request received (INVOKE) -> Session: '{session_id}', Persona: '{persona}', Input: '{user_input}'")

    config = {"configurable": {"session_id": session_id}}

    response_message = await conversation_chain.ainvoke(
        {
            "input": user_input,
            "persona": persona
        },
        config=config
    )

    clean_response = filter_allowed_text(response_message.content)
    logger.info(f"Invoke for session '{session_id}' completed successfully.")
    return clean_response