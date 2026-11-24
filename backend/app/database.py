import json
import sqlite3

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.config import DATABASE_PATH, DEFAULT_SYSTEM_PROMPT


def get_timestamp():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_db():
    if DATABASE_PATH != ":memory:":
        db_path = Path(DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                system_prompt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id)
                    REFERENCES sessions(session_id)
                    ON DELETE CASCADE
            )
        """)

        db.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session
            ON messages(session_id, id)
        """)


def create_session(session_id, system_prompt=None):
    # Always store a valid system prompt for new sessions.
    active_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT

    with get_db() as db:
        db.execute(
            """
            INSERT INTO sessions (
                session_id,
                system_prompt,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (session_id, active_prompt, get_timestamp()),
        )


def get_session(session_id):
    with get_db() as db:
        row = db.execute(
            """
            SELECT session_id, system_prompt, created_at
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

        return dict(row) if row else None


def update_system_prompt(session_id, system_prompt):
    with get_db() as db:
        db.execute(
            """
            UPDATE sessions
            SET system_prompt = ?
            WHERE session_id = ?
            """,
            (system_prompt, session_id),
        )


def add_message(session_id, role, content, metadata=None):
    metadata_json = (
        json.dumps(metadata) if metadata is not None else None
    )

    with get_db() as db:
        db.execute(
            """
            INSERT INTO messages (
                session_id,
                role,
                content,
                metadata,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                metadata_json,
                get_timestamp(),
            ),
        )


def get_messages(session_id):
    with get_db() as db:
        rows = db.execute(
            """
            SELECT id, session_id, role, content, metadata, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,),
        ).fetchall()

        result = []

        for row in rows:
            message = dict(row)

            if message["metadata"]:
                message["metadata"] = json.loads(message["metadata"])

            result.append(message)

        return result


def check_database():
    with get_db() as db:
        db.execute("SELECT 1").fetchone()

    return True
