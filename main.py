# main.py
import uvicorn
from fastapi import FastAPI

from api.routers import chat_router
from utils import logger

app = FastAPI(
    title="Conversational AI Agent Server",
    description="A dynamic multi-persona conversational agent server built with FastAPI and LangChain.",
    version="1.0.0",
)

app.include_router(chat_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """
    Basic health check endpoint to confirm the server is running.
    """
    return {"status": "ok", "message": "AI Companion server is running."}


if __name__ == "__main__":
    logger.info("AI Companion server is starting up...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
