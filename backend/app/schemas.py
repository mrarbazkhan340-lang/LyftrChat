
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# --------------------------------------------------
# Chat request
# --------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str = Field(
        min_length=1,
        max_length=128
    )

    message: str = Field(
        min_length=1,
        max_length=4000
    )

    system_prompt: Optional[str] = None

    @field_validator("session_id", "message")
    @classmethod
    def validate_required_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty.")

        return value

    @field_validator("system_prompt")
    @classmethod
    def validate_system_prompt(cls, value):
        if value is not None:
            value = value.strip()

        return value or None


# --------------------------------------------------
# Response metadata
# --------------------------------------------------

class ResponseMetadata(BaseModel):
    resolution_source: Literal[
        "LIVE_INFERENCE",
        "LLM_CACHE"
    ]

    model: str

    latency_ms: int = Field(ge=0)

    input_tokens: int = Field(ge=0)

    output_tokens: int = Field(ge=0)

    key_id: Optional[str] = None

    fallback_attempts: int = Field(ge=0)


# --------------------------------------------------
# Chat response
# --------------------------------------------------

class ChatResponse(BaseModel):
    session_id: str
    reply: str = Field(min_length=1)
    metadata: ResponseMetadata


# --------------------------------------------------
# Session history
# --------------------------------------------------

class MessageResponse(BaseModel):
    role: Literal["user", "assistant"]

    content: str

    metadata: Optional[ResponseMetadata] = None


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: list[MessageResponse]


# --------------------------------------------------
# Health response
# --------------------------------------------------

class HealthResponse(BaseModel):
    status: Literal["ok"]

    keys_configured: int

    cache_enabled: bool
