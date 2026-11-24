
import time

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import (
    ALLOWED_ORIGINS,
    API_KEY_POOL,
    APP_NAME,
    APP_VERSION,
    ENABLE_FAILURE_SIMULATION,
)
from app.database import (
    add_message,
    check_database,
    create_session,
    get_messages,
    get_session,
    initialize_database,
    update_system_prompt,
)
from app.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MessageResponse,
    SessionHistoryResponse,
)
from app.services.llm_service import (
    AllProvidersUnavailable,
    generate_response,
    parse_failure_header,
)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="LLM chatbot with API key failover and response caching.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/health", response_model=HealthResponse)
def health_check():
    try:
        check_database()
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="database unavailable",
        )

    if len(API_KEY_POOL) < 2:
        raise HTTPException(
            status_code=503,
            detail="at least two API keys must be configured",
        )

    return {
        "status": "ok",
        "keys_configured": len(API_KEY_POOL),
        "cache_enabled": True,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    x_simulate_failure: str | None = Header(default=None),
):
    started_at = time.perf_counter()

    message = request.message.strip()
    session_id = request.session_id.strip()

    try:
        simulated_failures = parse_failure_header(
            x_simulate_failure,
            ENABLE_FAILURE_SIMULATION,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error))

    session = get_session(session_id)

    if session is None:
        create_session(session_id, request.system_prompt)
        session = get_session(session_id)
    elif request.system_prompt is not None:
        update_system_prompt(session_id, request.system_prompt)
        session = get_session(session_id)

    history_rows = get_messages(session_id)

    history = [
        {"role": row["role"], "content": row["content"]}
        for row in history_rows
    ]

    active_system_prompt = (
        session["system_prompt"] if session else None
    )

    try:
        result = generate_response(
            user_message=message,
            history=history,
            system_prompt=active_system_prompt,
            simulated_failures=simulated_failures,
        )
    except AllProvidersUnavailable:
        raise HTTPException(
            status_code=503,
            detail="all providers unavailable",
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="all providers unavailable",
        )

    metadata = result["metadata"]
    metadata["latency_ms"] = int(
        (time.perf_counter() - started_at) * 1000
    )

    # Save only after a successful LLM response.
    add_message(session_id, "user", message)
    add_message(
        session_id,
        "assistant",
        result["reply"],
        metadata,
    )

    return {
        "session_id": session_id,
        "reply": result["reply"],
        "metadata": metadata,
    }


@app.get(
    "/sessions/{session_id}/messages",
    response_model=SessionHistoryResponse,
)
def session_messages(session_id: str):
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="session not found",
        )

    rows = get_messages(session_id)

    messages = [
        MessageResponse(
            role=row["role"],
            content=row["content"],
            metadata=row["metadata"],
        )
        for row in rows
    ]

    return {
        "session_id": session_id,
        "messages": messages,
    }
