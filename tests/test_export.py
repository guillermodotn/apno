"""Tests for the JSON export utility."""

import json
import os

from apno.utils.database import (
    get_practice_sessions,
    save_contraction,
    save_practice_session,
)
from apno.utils.export import export_sessions_json


class TestExportJson:
    def test_empty_database(self, tmp_db, monkeypatch):
        monkeypatch.setenv("APNO_DEV", "1")
        result = export_sessions_json()
        assert result == ""

    def test_exports_file(self, tmp_db, tmp_path, monkeypatch):
        monkeypatch.setenv("APNO_DEV", "1")
        monkeypatch.chdir(tmp_path)

        save_practice_session(training_type="free", duration_seconds=90.0)

        filepath = export_sessions_json()
        assert filepath != ""
        assert os.path.exists(filepath)
        assert filepath.endswith(".json")

    def test_json_structure(self, tmp_db, tmp_path, monkeypatch):
        monkeypatch.setenv("APNO_DEV", "1")
        monkeypatch.chdir(tmp_path)

        save_practice_session(
            training_type="free",
            duration_seconds=90.0,
            rounds_completed=1,
            parameters={"hold_time": 90},
            completed=True,
        )

        filepath = export_sessions_json()
        with open(filepath) as f:
            data = json.load(f)

        assert data["app"] == "Apno"
        assert "version" in data
        assert "exported_at" in data
        assert data["total_sessions"] == 1

        session = data["sessions"][0]
        assert session["training_type"] == "Free Training"
        assert session["duration_seconds"] == 90.0
        assert session["duration_formatted"] == "1:30"
        assert session["completed"] is True
        assert session["parameters"]["hold_time"] == 90

    def test_training_type_names(self, tmp_db, tmp_path, monkeypatch):
        monkeypatch.setenv("APNO_DEV", "1")
        monkeypatch.chdir(tmp_path)

        save_practice_session(training_type="o2", duration_seconds=600.0)
        save_practice_session(training_type="co2", duration_seconds=500.0)
        save_practice_session(training_type="free", duration_seconds=90.0)

        filepath = export_sessions_json()
        with open(filepath) as f:
            data = json.load(f)

        types = {s["training_type"] for s in data["sessions"]}
        assert types == {"CO2 Table", "O2 Table", "Free Training"}

    def test_includes_contractions(self, tmp_db, tmp_path, monkeypatch):
        monkeypatch.setenv("APNO_DEV", "1")
        monkeypatch.chdir(tmp_path)

        save_practice_session(training_type="free", duration_seconds=90.0)
        sessions = get_practice_sessions(limit=1)
        session_id = sessions[0]["id"]

        save_contraction(session_id, 45.2)
        save_contraction(session_id, 62.8)

        filepath = export_sessions_json()
        with open(filepath) as f:
            data = json.load(f)

        contractions = data["sessions"][0]["contractions"]
        assert len(contractions) == 2
        assert contractions[0]["seconds_into_hold"] == 45.2
        assert contractions[1]["seconds_into_hold"] == 62.8
