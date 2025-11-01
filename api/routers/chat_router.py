from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from api.services import chat_service
from models.request_models import ChatRequest
from models.response_models import ChatResponse
from utils import AppException, logger

router = APIRouter()


@router.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    API endpoint for streaming chat responses.
    """

    generator = chat_service.handle_chat_stream(
        session_id=request.session_id,
        user_id=request.user_id,
        user_input=request.input,
        persona=request.persona,
        background_tasks=background_tasks
    )
    return StreamingResponse(
        generator,
        media_type="text/plain; charset=utf-8"
    )


@router.post("/chat/invoke", response_model=ChatResponse, tags=["Chat"])
async def chat_invoke(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    API endpoint for non-streaming (invoke) chat responses.
    """
    try:
        response_text = await chat_service.handle_chat_invoke(
            session_id=request.session_id,
            user_id=request.user_id,
            user_input=request.input,
            persona=request.persona,
            background_tasks=background_tasks
        )
        return ChatResponse(response=response_text)

    except AppException as e:
        logger.warning(
            f"Handled known application error for session '{request.session_id}': {e.message}"
        )
        raise HTTPException(status_code=400, detail=e.message)

    except Exception as e:
        logger.error(
            f"An unexpected error occurred for session '{request.session_id}'!",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")

