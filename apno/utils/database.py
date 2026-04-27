"""SQLite database for persisting app data."""

import json
import os
import sqlite3
from pathlib import Path

from kivy.utils import platform


def get_data_dir() -> Path:
    """Get the platform-appropriate data directory.

    In development mode (APNO_DEV=1), uses the project directory.
    Otherwise uses the platform-appropriate location:
    - Linux/Desktop: ~/.local/share/apno (or XDG_DATA_HOME)
    - Android: app storage path
    - iOS: documents directory
    """
    # Development mode: use project directory
    if os.environ.get("APNO_DEV"):
        return Path(__file__).parent.parent.parent

    if platform == "android":
        from android.storage import app_storage_path  # type: ignore

        return Path(app_storage_path())
    elif platform == "ios":
        from pyobjus import autoclass  # type: ignore

        ns_search = autoclass("NSSearchPathForDirectoriesInDomains")
        docs = ns_search(9, 1, True).objectAtIndex_(0)
        return Path(docs)
    else:
        # Desktop: use XDG data home or fallback
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            data_dir = Path(xdg_data) / "apno"
        else:
            data_dir = Path.home() / ".local" / "share" / "apno"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir


def get_db_path() -> Path:
    """Get the path to the SQLite database file."""
    return get_data_dir() / "apno.db"


def get_connection() -> sqlite3.Connection:
    """Get a connection to the database."""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                training_type TEXT NOT NULL,
                score REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_scores_training_type
            ON scores (training_type)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS practice_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                training_type TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_seconds REAL,
                rounds_completed INTEGER,
                parameters TEXT,
                completed INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_practice_sessions_training_type
            ON practice_sessions (training_type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_practice_sessions_completed_at
            ON practice_sessions (completed_at)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                seconds_into_hold REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES practice_sessions (id)
                    ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_contractions_session_id
            ON contractions (session_id)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_score(training_type: str, score: float) -> None:
    """Save a score to the database.

    Args:
        training_type: The type of training (e.g., 'free', 'o2', 'co2')
        score: The score/time achieved in seconds
    """
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO scores (training_type, score) VALUES (?, ?)",
            (training_type, score),
        )
        conn.commit()
    finally:
        conn.close()


def get_best_score(training_type: str) -> float | None:
    """Get the best (highest) score for a training type.

    Args:
        training_type: The type of training (e.g., 'free', 'o2', 'co2')

    Returns:
        The best score in seconds, or None if no scores exist
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT MAX(score) as best FROM scores WHERE training_type = ?",
            (training_type,),
        )
        row = cursor.fetchone()
        return row["best"] if row and row["best"] is not None else None
    finally:
        conn.close()


def get_best_free_duration() -> float | None:
    """Get the longest completed free training hold duration.

    Returns:
        The best duration in seconds, or None if no completed free sessions
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT MAX(duration_seconds) as best FROM practice_sessions "
            "WHERE training_type = 'free' AND completed = 1"
        )
        row = cursor.fetchone()
        return row["best"] if row and row["best"] is not None else None
    finally:
        conn.close()


def save_practice_session(
    training_type: str,
    duration_seconds: float | None = None,
    rounds_completed: int | None = None,
    parameters: dict | None = None,
    completed: bool = True,
) -> int:
    """Save a practice session to the database.

    Args:
        training_type: The type of training ('co2', 'o2', 'free')
        duration_seconds: Total session duration in seconds
        rounds_completed: Number of rounds completed
        parameters: Dictionary of training parameters specific to the type
        completed: Whether the session was completed (not stopped early)

    Returns:
        The ID of the inserted session
    """
    conn = get_connection()
    try:
        params_json = json.dumps(parameters) if parameters else None
        cursor = conn.execute(
            """
            INSERT INTO practice_sessions
            (training_type, duration_seconds, rounds_completed, parameters, completed)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                training_type,
                duration_seconds,
                rounds_completed,
                params_json,
                1 if completed else 0,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_practice_sessions(
    training_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Get practice sessions from the database.

    Args:
        training_type: Optional filter by training type
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip (for pagination)

    Returns:
        List of session dictionaries
    """
    conn = get_connection()
    try:
        if training_type:
            cursor = conn.execute(
                """
                SELECT id, training_type, completed_at, duration_seconds,
                       rounds_completed, parameters, completed
                FROM practice_sessions
                WHERE training_type = ?
                ORDER BY completed_at DESC
                LIMIT ? OFFSET ?
                """,
                (training_type, limit, offset),
            )
        else:
            cursor = conn.execute(
                """
                SELECT id, training_type, completed_at, duration_seconds,
                       rounds_completed, parameters, completed
                FROM practice_sessions
                ORDER BY completed_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )

        sessions = []
        for row in cursor.fetchall():
            session = dict(row)
            if session["parameters"]:
                session["parameters"] = json.loads(session["parameters"])
            sessions.append(session)
        return sessions
    finally:
        conn.close()


def get_session_by_id(session_id: int) -> dict | None:
    """Get a single practice session by its ID.

    Args:
        session_id: The session ID to look up

    Returns:
        Session dictionary with parsed parameters, or None if not found
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, training_type, completed_at, duration_seconds,
                   rounds_completed, parameters, completed
            FROM practice_sessions
            WHERE id = ?
            """,
            (session_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        session = dict(row)
        if session["parameters"]:
            session["parameters"] = json.loads(session["parameters"])
        return session
    finally:
        conn.close()


def get_training_types_by_date(days: int = 30) -> dict[str, set[str]]:
    """Get the training types done per day for the last N days.

    Args:
        days: Number of days to look back

    Returns:
        Dictionary mapping date strings to sets of training types done that day
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT date(completed_at) as session_date, training_type
            FROM practice_sessions
            WHERE completed_at >= date('now', ?)
              AND training_type IN ('co2', 'o2')
            GROUP BY date(completed_at), training_type
            ORDER BY session_date DESC
            """,
            (f"-{days} days",),
        )

        result: dict[str, set[str]] = {}
        for row in cursor.fetchall():
            date_str = row["session_date"]
            training_type = row["training_type"]
            if date_str not in result:
                result[date_str] = set()
            result[date_str].add(training_type)
        return result
    finally:
        conn.close()


def save_contraction(session_id: int, seconds_into_hold: float) -> int:
    """Record a contraction during a breath hold.

    Args:
        session_id: The ID of the practice session
        seconds_into_hold: Time in seconds when contraction occurred

    Returns:
        The ID of the inserted contraction
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO contractions (session_id, seconds_into_hold) VALUES (?, ?)",
            (session_id, seconds_into_hold),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_contractions_for_session(session_id: int) -> list[dict]:
    """Get all contractions for a specific session.

    Args:
        session_id: The practice session ID

    Returns:
        List of contraction dictionaries sorted by time
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT id, seconds_into_hold, created_at
            FROM contractions
            WHERE session_id = ?
            ORDER BY seconds_into_hold ASC
            """,
            (session_id,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_contraction_count_for_session(session_id: int) -> int:
    """Get the count of contractions for a session.

    Args:
        session_id: The practice session ID

    Returns:
        Number of contractions recorded
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT COUNT(*) as count FROM contractions WHERE session_id = ?",
            (session_id,),
        )
        row = cursor.fetchone()
        return row["count"] if row else 0
    finally:
        conn.close()


def save_settings(settings: dict[str, str]) -> None:
    """Save multiple settings to the database.

    Args:
        settings: Dictionary of key-value pairs
    """
    conn = get_connection()
    try:
        for key, value in settings.items():
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value)),
            )
        conn.commit()
    finally:
        conn.close()


def load_settings() -> dict[str, str]:
    """Load all settings from the database.

    Returns:
        Dictionary of key-value pairs
    """
    conn = get_connection()
    try:
        cursor = conn.execute("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in cursor.fetchall()}
    finally:
        conn.close()


# Initialize database on module import
init_db()
