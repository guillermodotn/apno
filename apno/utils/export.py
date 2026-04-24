"""Data export utility for training sessions."""

import json
import os
from datetime import datetime

from kivy.utils import platform

from apno import __version__
from apno.utils.database import (
    get_contractions_for_session,
    get_practice_sessions,
)

# Internal training type -> user-facing name
_TYPE_NAMES = {
    "o2": "CO2 Table",
    "co2": "O2 Table",
    "free": "Free Training",
}


def _get_export_dir():
    """Get the directory for exported files.

    In dev mode (APNO_DEV=1), exports to the current working directory.
    On Android, exports to the Download folder.
    On desktop, exports to ~/Downloads.
    """
    if os.environ.get("APNO_DEV"):
        return os.getcwd()

    if platform == "android":
        from android.storage import primary_external_storage_path  # type: ignore

        export_dir = os.path.join(primary_external_storage_path(), "Download")
    else:
        export_dir = os.path.expanduser("~/Downloads")

    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def export_sessions_json() -> str:
    """Export all training sessions to a JSON file.

    Includes full session data, parameters, and contraction timestamps.

    Returns:
        The file path of the exported JSON file, or empty string if no data.
    """
    sessions = get_practice_sessions(limit=10000)
    if not sessions:
        return ""

    export_sessions = []
    for session in sessions:
        duration = session.get("duration_seconds", 0) or 0
        mins, secs = divmod(int(duration), 60)
        training_type = session.get("training_type", "")

        # Get contractions with timestamps
        contractions = get_contractions_for_session(session["id"])
        contraction_data = [
            {"seconds_into_hold": c["seconds_into_hold"]} for c in contractions
        ]

        export_sessions.append(
            {
                "id": session["id"],
                "training_type": _TYPE_NAMES.get(training_type, training_type),
                "date": session.get("completed_at", ""),
                "duration_seconds": duration,
                "duration_formatted": f"{mins}:{secs:02d}",
                "rounds_completed": session.get("rounds_completed", 0),
                "completed": bool(session.get("completed", 1)),
                "parameters": session.get("parameters", {}),
                "contractions": contraction_data,
            }
        )

    now = datetime.now()
    export_data = {
        "app": "Apno",
        "version": __version__,
        "exported_at": now.isoformat(),
        "total_sessions": len(export_sessions),
        "sessions": export_sessions,
    }

    # Save to file
    export_dir = _get_export_dir()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"apno_export_{timestamp}.json"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    return filepath
