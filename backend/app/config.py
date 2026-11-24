
import os
from pathlib import Path

from dotenv import load_dotenv


# --------------------------------------------------
# Load environment variables from project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# Application settings
# --------------------------------------------------

APP_NAME = "LyftrChat"
APP_VERSION = "1.0.0"

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "gemini/gemini-3.5-flash-lite"
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, accurate and friendly AI assistant. "
    "Answer clearly and concisely."
)


# --------------------------------------------------
# API key pool
# --------------------------------------------------

LLM_API_KEYS = [
    key.strip()
    for key in os.getenv("LLM_API_KEYS", "").split(",")
    if key.strip()
]

API_KEY_POOL = [
    {
        "key_id": f"key_{index + 1}",
        "api_key": api_key
    }
    for index, api_key in enumerate(LLM_API_KEYS)
]


# --------------------------------------------------
# Database settings
# --------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./app.db"
)


def get_database_path():
    """
    Convert SQLite DATABASE_URL into a filesystem path.

    sqlite:///./app.db  -> ./app.db
    sqlite:////data/app.db -> /data/app.db
    """

    prefix = "sqlite:///"

    if not DATABASE_URL.startswith(prefix):
        raise ValueError("Only SQLite DATABASE_URL is supported.")

    return DATABASE_URL[len(prefix):]


DATABASE_PATH = get_database_path()


# --------------------------------------------------
# CORS settings
# --------------------------------------------------

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000"
    ).split(",")
    if origin.strip()
]


# --------------------------------------------------
# Failure simulation settings
# --------------------------------------------------

ENABLE_FAILURE_SIMULATION = (
    os.getenv("ENABLE_FAILURE_SIMULATION", "false").lower()
    == "true"
)


# --------------------------------------------------
# Validation helpers
# --------------------------------------------------

def get_config_status():
    return {
        "app_name": APP_NAME,
        "model": LLM_MODEL,
        "keys_configured": len(API_KEY_POOL),
        "cache_enabled": True,
        "failure_simulation_enabled": ENABLE_FAILURE_SIMULATION
    }
