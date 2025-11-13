# Conversational AI Agent Server

This project is a modular conversational AI server built with Python, FastAPI, and LangChain. It is designed to serve multiple, dynamic "personas" (e.g., Miki, Alex, Kaito) powered by OpenAI-compatible LLMs exposed via OpenRouter or Groq.

The server is stateful, maintaining conversation history via Redis, streams responses token-by-token, provides a non-streaming alternative, and ensures clean, TTS-ready output.

## Key Features

* **Configurable LLM Backend:** Easily switch between OpenRouter or Groq models via environment variables.
* **Dynamic Persona System:** The client can choose the agent's personality (e.g., `miki`, `alex`, `kaito`) on a per-request basis.
* **Jinja2 Prompts:** All system prompts are managed in external `.j2` template files, making them easy to edit and expand.
* **Streaming & Non-Streaming API:** Offers both a real-time `/chat/stream` endpoint and a standard `/chat/invoke` endpoint.
* **TTS-Ready Output Filter:** Automatically strips non-speakable characters (emojis, etc.) from the LLM response, ensuring clean text for Text-to-Speech engines.
* **Stateful Conversations:** Leverages Redis (`RedisChatMessageHistory`) to maintain persistent conversation history for each unique `session_id`.
* **Windowed Memory:** Automatically trims the prompt's context to the last `N` messages (configurable in `.env`) to ensure fast responses.
* **Clean Architecture:** Follows a service-oriented pattern (API Router -> Business Logic Service -> Agent Layer) with clear package interfaces (`__init__.py`).
* **Custom Exception Handling:** Includes a custom exception framework (`utils/exceptions.py`) for graceful error management.
* **Detailed Colored Logging:** Provides structured, colored logs (using `colorlog`) including DEBUG level details on prompts and responses (tunable via `LOG_LEVEL`).

## Project Structure

```text
/
├── agents/             # Core LangChain chain logic (conversation_agent.py)
├── api/                # FastAPI application
│   ├── routers/        # API endpoint definitions (chat_router.py)
│   └── services/       # Business logic (chat_service.py)
├── config/             # Global server configuration and LLM loader
│   ├── settings.py     # Pydantic-based Settings (env-driven)
│   └── llm.py          # LLM client loading & interface
├── memory/             # Redis memory configuration & interface (short_term.py)
├── models/             # Pydantic request/response models (request_models.py, response_models.py)
├── prompt_templates/   # Jinja2 system prompts (.j2 files)
├── utils/              # Utility code (exceptions.py, logging.py, helper.py, __init__.py)
├── .env                # Local environment variables (GITIGNORED)
├── .gitignore          # Specifies intentionally untracked files
├── main.py             # FastAPI server entrypoint
├── requirements.txt    # Python dependencies
└── readme.md           # This file
```

## Setup and Installation

### 1. Prerequisites

Before you begin, you must have the following services running or available:

* **LLM Provider:**
  * **OpenRouter:** You need an API key from [OpenRouter.ai](https://openrouter.ai/).
  * **Groq:** You need an API key from [Groq](https://groq.com/).
* **Redis:** A Redis server must be running and accessible (e.g. `redis://localhost:6379/0`).

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

4.  Create a `.env` file in the project root directory. Example:

    ```env
    # LLM configuration
    LLM_PROVIDER="openrouter"                             # or "groq"
    LLM_MODEL="meta-llama/llama-3.1-8b-instruct"          # example model

    # Provider API keys
    OPENROUTER_API_KEY="sk-or-..."                        # required if LLM_PROVIDER="openrouter"
    GROQ_API_KEY="gsk_..."                                # required if LLM_PROVIDER="groq"

    # Redis
    REDIS_URL="redis://localhost:6379/0"
    DEFAULT_SESSION_ID="default_session"
    MEMORY_WINDOW_SIZE=16
    REDIS_TTL_SECONDS=1800

    # Logging
    LOG_LEVEL="INFO"                                      # or "DEBUG" for development
    ```

## Running the Server

Ensure your `.env` file is configured correctly and prerequisite services (Redis, LLM provider) are running. Start the FastAPI server from the project's root directory:

```bash
python main.py
```

The server will be live at `http://127.0.0.1:8000`. You can view the API documentation at `http://127.0.0.1:8000/docs`.

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
curl -N -X POST "http://127.0.0.1:8000/api/chat/stream" \
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
curl -X POST "http://127.0.0.1:8000/api/chat/invoke" \
     -H "Content-Type: "application/json" \
     -d '{
           "input": "Hello! What's your name?",
           "session_id": "user_session_123",
           "persona": "miki"
         }'
```
