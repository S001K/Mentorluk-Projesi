# Conversational AI Agent Server

This project is a modular conversational AI server built with Python, FastAPI, and LangChain. It is designed to serve multiple, dynamic "personas" (e.g., Miki, Alex, Kaito) powered by either a local LLM via Ollama or external models via OpenRouter, configurable at startup.

The server is stateful, maintaining conversation history via Redis, streams responses token-by-token, provides a non-streaming alternative, and ensures clean, TTS-ready output.

## Key Features

* **Configurable LLM Backend:** Easily switch between local Ollama models or external OpenRouter models via simple settings in `config.py`.
* **Dynamic Persona System:** The client can choose the agent's personality (e.g., `miki`, `alex`, `kaito`) on a per-request basis.
* **Jinja2 Prompts:** All system prompts are managed in external `.j2` template files, making them easy to edit and expand.
* **Streaming & Non-Streaming API:** Offers both a real-time `/chat/stream` endpoint and a standard `/chat/invoke` endpoint.
* **TTS-Ready Output Filter:** Automatically strips non-speakable characters (emojis, etc.) from the LLM response, ensuring clean text for Text-to-Speech engines.
* **Stateful Conversations:** Leverages Redis (`RedisChatMessageHistory`) to maintain persistent conversation history for each unique `session_id`.
* **Windowed Memory:** Automatically trims the prompt's context to the last `N` messages (configurable in `config.py`) to ensure fast responses.
* **Clean Architecture:** Follows a service-oriented pattern (API Router -> Business Logic Service -> Agent Layer) with clear package interfaces (`__init__.py`).
* **Custom Exception Handling:** Includes a custom exception framework (`utils/exceptions.py`) for graceful error management.
* **Detailed Colored Logging:** Provides structured, colored logs (using `colorlog`) including DEBUG level details on prompts and responses.

## Project Structure

```
/
├── agents/             # Core LangChain chain logic (conversation_agent.py)
├── api/                # FastAPI application
│   ├── routers/        # API endpoint definitions (chat_router.py)
│   └── services/       # Business logic (chat_service.py)
├── llm/                # LLM client loading & interface (loader.py, __init__.py)
├── memory/             # Redis memory configuration & interface (short_term.py, __init__.py)
├── models/             # Pydantic request/response models & interface (request_models.py, __init__.py)
├── prompt_templates/   # Jinja2 system prompts (.j2 files)
├── utils/              # Utility code & interface (exceptions.py, logging.py, helper.py, __init__.py)
├── .env                # Local environment variables (GITIGNORED)
├── .gitignore          # Specifies intentionally untracked files
├── config.py           # Global server configuration (reads .env)
├── main.py             # FastAPI server entrypoint
├── requirements.txt    # Python dependencies
└── readme.md           # This file
```

## Setup and Installation

### 1. Prerequisites

Before you begin, you must have the following services running or available:

* **Ollama (If using):** The server must be running (`ollama serve`).
* **LLM Model (If using Ollama):** You must pull a model. The project defaults to `gemma3:1b-it-qat`.
    ```bash
    ollama gemma3:1b-it-qat
    ```
* **OpenRouter API Key (If using):** You need an API key from [OpenRouter.ai](https://openrouter.ai/).
* **Redis:** A Redis server must be running and accessible (defaults to `redis://localhost:6379`).

### 2. Installation

1.  Clone this repository:
    ```bash
    git clone <https://github.com/S001K/Mentorluk-Projesi.git>
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

4.  Create a `.env` file in the project root directory. Copy the contents from this example or create it manually with the necessary variables (see Configuration section below). Example:
    ```env
    # .env file
    LLM_PROVIDER="ollama"
    LLM_MODEL="gemma3:1b-it-qat"
    # OPENROUTER_API_KEY="sk-or-..." # Only needed if LLM_PROVIDER="openrouter"
    REDIS_URL="redis://localhost:6379/0"
    ```

## Configuration

Configuration is primarily managed via environment variables loaded from the `.env` file into `config.py`.

* `LLM_PROVIDER`: Set to `"ollama"` or `"openrouter"` to select the LLM backend.
* `LLM_MODEL`: The specific model name to use.
    * For Ollama: e.g., `"gemma3:1b-it-qat"`
    * For OpenRouter: e.g., `"meta-llama/llama-3.3-70b-instruct:free"`
* `OPENROUTER_API_KEY`: Your API key from OpenRouter (only required if `LLM_PROVIDER` is `"openrouter"`).
* `REDIS_URL`: The connection string for your Redis server.
* `MEMORY_WINDOW_SIZE`: The number of messages (user + AI) to send to the LLM in each request.
* `PERSONA_PROMPTS`: (Defined in `config.py`) Maps persona keys (like "miki") to their `.j2` template files.

## Running the Server

Ensure your `.env` file is configured correctly and prerequisite services (Ollama/Redis) are running. Start the FastAPI server from the project's root directory:

```bash
python main.py
```

The server will be live at `http://120.0.0.1:8000`. You can view the API documentation at `http://120.0.0.1:8000/docs`.

## API Usage

Two endpoints are available:

1.  `POST /api/chat/stream`: Streams the response token by token (requires a client that supports streaming).
2.  `POST /api/chat/invoke`: Returns the complete response in a single JSON object.

Both endpoints accept the same JSON request body:

```json
{
  "input": "Your message here",
  "session_id": "unique_session_identifier",
  "persona": "alex" // Or "miki", "kaito", etc.
}
```

### Example `curl` Request (Streaming)

The `-N` flag is crucial for `curl` to display the stream.

```bash
curl -N -X POST "http://120.0.0.1:8000/api/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{
           "input": "Hey, what do you think of this rain?",
           "session_id": "user_session_456",
           "persona": "kaito"
         }'
```

### Example `curl` Request (Non-Streaming)

This returns a JSON response like `{"response": "The AI's full answer."}`.

```bash
curl -X POST "http://120.0.0.1:8000/api/chat/invoke" \
     -H "Content-Type: application/json" \
     -d '{
           "input": "Hello! What's your name?",
           "session_id": "user_session_123",
           "persona": "miki"
         }'
```