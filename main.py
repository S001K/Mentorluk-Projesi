import uvicorn
from fastapi import FastAPI

# Import the router from the api module
from api.routers import chat_router

# Create the FastAPI app
app = FastAPI(
    title="Conversational AI Server",
    description="A FastAPI server for the LangChain conversational agent.",
    version="1.0.0",
)

# All routes in 'chat_router.router' will be added to the app
app.include_router(chat_router.router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to the AI Companion Conversation Server"}

# The entry point to run the server
if __name__ == "__main__":
    print("Starting server...")
    # This will run the server on http://127.0.0.1:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)

