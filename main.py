import uvicorn
from fastapi import FastAPI
from utils import logger
from api.routers import chat_router

app = FastAPI(
    title="Conversational AI Agent Server",
    description="A dynamic persona agent server based on Ollama and LangChain.",
    version="1.0.0"
)

app.include_router(chat_router.router, prefix="/api")

@app.get("/", tags=["Health"])
async def root():
    """
    Basic health check endpoint to confirm the server is running.
    """
    return {"status": "ok", "message": "AI Companion server is running."}

if __name__ == "__main__":
    logger.info("AI Companion server is starting up...")
    uvicorn.run(app, host="127.0.0.1", port=8000)