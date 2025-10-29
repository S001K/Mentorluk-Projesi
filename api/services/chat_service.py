from agents.conversation_agent import conversation_chain


async def handle_chat_stream(session_id: str, user_input: str, persona: str):
    """
    Handles the streaming chat logic by invoking the conversation chain.
    This is an async generator that yields response chunks.
    """
    # Create the configuration for the chain
    config = {"configurable": {"session_id": session_id}}

    # Use .astream() to asynchronously stream the response
    async for chunk in conversation_chain.astream(
            {
                "input": user_input,
                "persona": persona
            },
            config=config
    ):
        # The chunk is an AIMessageChunk
        # We yield its content as it arrives
        yield chunk.content