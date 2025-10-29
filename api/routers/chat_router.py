from fastapi import APIRouter
from fastapi.responses import StreamingResponse

# Import the service that contains the core logic
from api.services import chat_service
# Import the request model
from models.request_models import ChatRequest

# Create a new router
router = APIRouter()


@router.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest):
    """
    API endpoint for streaming chat responses.
    """
    # 1. Call the service to get the async generator
    generator = chat_service.handle_chat_stream(
        session_id=request.session_id,
        user_input=request.input,
        persona=request.persona
    )

    # 2. Return the generator in a StreamingResponse
    return StreamingResponse(generator, media_type="text/plain")