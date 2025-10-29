# Conversational AI Agent Server

This project is a modular conversational AI server built with Python, FastAPI, and LangChain. It is designed to serve multiple, dynamic "personas" (e.g., Miki, Alex, Kaito) currently powered by a local LLM via Ollama.

The server is stateful, maintaining conversation history via Redis, and streams responses token-by-token over a clean, service-oriented API.

## Key Features

* **Dynamic Persona System:** The client can choose the agent's personality (e.g., `miki`, `alex`, `kaito`) on a per-request basis.
* **Jinja2 Prompts:** All system prompts are managed in external `.j2` template files, making them easy to edit and expand.
* **Streaming API:** Uses FastAPI's `StreamingResponse` and LangChain's `.astream()` for real-time, token-by-token chat responses.
* **Stateful Conversations:** Leverages Redis (`RedisChatMessageHistory`) to maintain persistent conversation history for each unique session.
* **Windowed Memory:** Automatically trims the prompt's context to the last `N` messages (configurable in `config.py`) to ensure fast responses and prevent context window overload.
* **Configurable Backend:** Easily connect to any local LLM served by Ollama (e.g., `gemma:2b`, `llama3`, etc.).
* **Clean Architecture:** Follows a service-oriented pattern (API Router -> Business Logic Service -> Agent Layer) for maintainability.

## Project Structure

```
/
├── agents/             # Core LangChain (LCEL) chain logic (conversation_agent.py)
├── api/                # FastAPI application
│   ├── routers/        # API endpoint definitions (chat_router.py)
│   └── services/       # Business logic (chat_service.py)
├── llm/                # Ollama client instance
├── memory/             # Redis memory configuration (short_term.py)
├── models/             # Pydantic request models (request_models.py)
├── prompt_templates/   # Jinja2 system prompts (.j2 files)
├── utils/              # Utility code
├── config.py           # Global server configuration
├── main.py             # FastAPI server entrypoint
└── readme.md           # This file
```

## Setup and Installation

### 1. Prerequisites

Before you begin, you must have the following services running:

* **Ollama:** The server must be running. You can start it with `ollama serve`.
* **LLM Model:** You must pull a model for Ollama to use. This project defaults to `gemma3:1b-it-qat`, which you can get with:
    ```bash
    ollama pull gemma3:1b-it-qat
    ```
* **Redis:** A Redis server must be running and accessible. The default configuration assumes `redis://localhost:6379`.

### 2. Installation

1.  Clone this repository:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

All main configuration is handled in the `config.py` file.

* `LLM_MODEL`: The name of the Ollama model to use (e.g., "gemma3:1b-it-qat").
* `REDIS_URL`: The connection string for your Redis server.
* `MEMORY_WINDOW_SIZE`: The number of messages (user + AI) to send to the LLM in each request.
* `PERSONA_PROMPTS`: The dictionary that maps persona keys (like "miki") to their corresponding `.j2` template files in the `prompt_templates` folder.

## Running the Server

Once your `config.py` is set up and your prerequisite services (Ollama, Redis) are running, you can start the FastAPI server from the project's root directory:

```bash
python main.py
```

The server will be live at `http://127.0.0.1:8000`. You can view the API documentation at `http://127.0.0.1:8000/docs`.

## API Usage

To interact with the agent, you must use an API client that supports streaming responses (e.g., `curl`, Postman, Insomnia).

The primary endpoint is `POST /api/chat/stream`.

### Example `curl` Request

This example shows how to send a message to the "alex" persona for a specific session. The `-N` flag is crucial for `curl` to display the stream as it arrives.

```bash
curl -N -X POST "http://127.0.0.1:8000/api/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{
           "input": "Hey, what do you think about playing video games?",
           "session_id": "user_session_456",
           "persona": "alex"
         }'
```

### Example Request (Miki Persona)

To talk to a different persona, simply change the `persona` key in your request body.

```bash
curl -N -X POST "http://127.0.0.1:8000/api/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{
           "input": "Hello! What's your name?",
           "session_id": "user_session_123",
           "persona": "miki"
         }'
```