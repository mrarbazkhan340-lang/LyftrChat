# LyftrChat — LLM Chatbot with Key Failover & Response Caching

LyftrChat is a full-stack AI chatbot built using React, FastAPI, LiteLLM, and SQLite. It supports automatic API key failover, response caching, multi-turn conversations, and token usage tracking.

## 1. Live URLs

- **Frontend:** https://lyftr-chat-five.vercel.app/
- **Backend:** https://lyftrchat.onrender.com
- **API Documentation:** https://lyftrchat.onrender.com/docs
- **Health Check:** https://lyftrchat.onrender.com/health
- **GitHub Repository:** https://github.com/mrarbazkhan340-lang/LyftrChat

## 2. Tech Stack

| Component | Technology |
|---|---|
| Frontend | React.js, Vite |
| Backend | Python, FastAPI |
| LLM Gateway | LiteLLM |
| AI Provider | Google Gemini |
| Database | SQLite |
| Caching | LiteLLM Local Cache |
| Containerization | Docker, Docker Compose |
| Deployment | Vercel, Render |

## 3. Run Locally

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker Desktop (for Docker setup)
- Google Gemini API keys (minimum 2)

### Environment Configuration

Clone the repository:

```bash
git clone https://github.com/mrarbazkhan340-lang/LyftrChat.git
cd LyftrChat
```

Create a `.env` file in the project root using `.env.example`.

Configure the following variables:

```env
LLM_API_KEYS=YOUR_GEMINI_KEY_1,YOUR_GEMINI_KEY_2
LLM_MODEL=gemini/gemini-3.5-flash-lite
DATABASE_URL=sqlite:///./app.db
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
ENABLE_FAILURE_SIMULATION=true
```

Never commit your actual API keys or `.env` file.

### Option A: Run with Docker (Recommended)

Build and start the application:

```bash
docker compose up --build -d
```

Access the application:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Stop the application:

```bash
docker compose down
```

The SQLite database is stored in a Docker named volume mounted at `/data`, allowing database persistence across container restarts.

### Option B: Run Without Docker

**Start the backend**

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```cmd
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

**Start the frontend**

Open another terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Start the development server:

```bash
npm run dev
```

Frontend: http://localhost:5173

## 4. Design Decisions

### API Key Failover

- Supports multiple Gemini API keys through environment variables.
- Uses LiteLLM to communicate with the configured LLM.
- Automatically attempts the next available key when a provider request fails.
- Handles simulated failures for testing HTTP 429 and 5xx scenarios.
- Returns an error when all configured providers are unavailable.

### Response Caching

- Uses LiteLLM's built-in local cache.
- Cache entries are based on the model and complete message history.
- Identical requests can reuse previously generated responses.
- Cache hits are identified as `LLM_CACHE`.
- Live model responses are identified as `LIVE_INFERENCE`.

### SQLite Database

- Stores conversation sessions and messages.
- Maintains multi-turn conversation history.
- Stores assistant response metadata, including token usage and model information.
- Creates database tables automatically during application startup.
- Uses a Docker volume for persistent database storage.

### Token Tracking

Each assistant response tracks:

- Input tokens
- Output tokens
- Model name
- Response latency
- Resolution source
- API key identifier
- Number of fallback attempts

## 5. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Application health and configuration status |
| POST | `/chat` | Send a message and receive an AI response |
| GET | `/sessions/{session_id}/messages` | Retrieve conversation history |

### POST /chat

Example request:

```json
{
  "session_id": "session-001",
  "message": "Explain Python in simple words."
}
```

Optional field:

```json
{
  "system_prompt": "You are a helpful assistant."
}
```

Example response structure:

```json
{
  "session_id": "session-001",
  "reply": "Python is a programming language...",
  "metadata": {
    "resolution_source": "LIVE_INFERENCE",
    "model": "gemini/gemini-3.5-flash-lite",
    "latency_ms": 1200,
    "input_tokens": 20,
    "output_tokens": 100,
    "key_id": "key_1",
    "fallback_attempts": 0
  }
}
```

## 6. Verification

The following application behaviors have been tested during development:

### Response Caching

1. Send a message in a conversation.
2. Start a new session.
3. Send the exact same message again.
4. Check the response metadata.

Expected result: `LLM_CACHE`.

### Multi-Turn Conversation

1. Send an initial message.
2. Ask a follow-up question in the same session.
3. Verify that the assistant uses the previous conversation context.
4. Retrieve the session history using the messages endpoint.

### API Key Failover

Failure simulation is controlled using:

```env
ENABLE_FAILURE_SIMULATION=true
```

Use the following request header:

```text
X-Simulate-Failure: key_1=429
```

Expected behavior:

- First API key simulates a 429 failure.
- The second API key is attempted.
- A successful response should report `key_id: key_2` and `fallback_attempts: 1`.

To simulate failure of all keys:

```text
X-Simulate-Failure: *=429
```

Expected result: HTTP 503 with:

```json
{
  "detail": "all providers unavailable"
}
```

Failure simulation should be disabled in production when it is no longer needed.

### Token Tracking

Check assistant message metadata for input tokens, output tokens, model, latency, and resolution source.

## 7. Project Structure

```text
LyftrChat/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── schemas.py
│   │   └── services/
│   │       └── llm_service.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml
├── Makefile
├── .env.example
├── .gitignore
└── README.md
```

## 8. Setup Used

- Developed using Visual Studio Code.
- Backend implemented with Python and FastAPI.
- Frontend implemented with React and Vite.
- LiteLLM integrated for LLM requests and caching.
- SQLite used for session and message persistence.
- Docker Compose used for local container orchestration.
- Git and GitHub used for version control.
- Frontend deployed on Vercel.
- Backend deployed on Render.

## 9. Bonus Features

- Clean and responsive chatbot interface.
- Optional custom system prompt.
- Session-based conversation management.
- Response metadata displayed in the frontend.
- API failure simulation for testing failover behavior.
- Docker-based deployment setup.

---

**Developed as part of the Lyftr AI Full Stack Developer Internship Assignment.**