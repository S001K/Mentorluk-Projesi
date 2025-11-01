"""
API Router for Memory Management
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

# Yeni memory servisini import et
from api.services import memory_service
from models.request_models import MemoryRequest
from utils import AppException, logger

router = APIRouter()

@router.post("/memory", status_code=status.HTTP_201_CREATED, tags=["Memory"])
async def add_new_memory(request: MemoryRequest):
    """
    API endpoint for *manually* adding a new fact (memory)
    to the agent's long-term semantic vector store.
    (This endpoint was moved from chat_router.py)
    """
    try:
        # Yeni memory_service'i çağır
        memory_service.handle_add_memory(
            text=request.text,
            user_id=request.user_id,
            persona=request.persona
        )
        return JSONResponse(
            content={"message": "Memory added successfully"},
            status_code=status.HTTP_201_CREATED
        )
    except AppException as e:
        logger.warning(f"Failed to add memory: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"An unexpected error occurred while adding memory!", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")