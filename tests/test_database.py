"""Tests for the database layer."""

from apno.utils.database import (
    get_best_free_duration,
    get_contraction_count_for_session,
    get_contractions_for_session,
    get_practice_sessions,
    get_session_by_id,
    get_training_types_by_date,
    init_db,
    load_settings,
    save_contraction,
    save_practice_session,
    save_score,
    save_settings,
)


class TestInitDb:
    def test_creates_database_file(self, tmp_db):
        assert tmp_db.exists()

    def test_idempotent(self, tmp_db):
        """Calling init_db twice should not raise."""
        init_db()
        assert tmp_db.exists()


class TestPracticeSessions:
    def test_save_and_retrieve(self, tmp_db):
        save_practice_session(
            training_type="free",
            duration_seconds=90.0,
            rounds_completed=1,
            parameters={"hold_time": 90},
            completed=True,
        )
        sessions = get_practice_sessions(limit=10)
        assert len(sessions) == 1
        assert sessions[0]["training_type"] == "free"
        assert sessions[0]["duration_seconds"] == 90.0
        assert sessions[0]["completed"] == 1

    def test_parameters_stored_as_json(self, tmp_db):
        params = {"hold_time": 60, "contraction_count": 2}
        save_practice_session(
            training_type="free",
            duration_seconds=60.0,
            rounds_completed=1,
            parameters=params,
        )
        sessions = get_practice_sessions(limit=1)
        assert sessions[0]["parameters"]["hold_time"] == 60
        assert sessions[0]["parameters"]["contraction_count"] == 2

    def test_multiple_sessions_ordered_by_date(self, tmp_db):
        save_practice_session(training_type="free", duration_seconds=30.0)
        save_practice_session(training_type="o2", duration_seconds=600.0)
        save_practice_session(training_type="co2", duration_seconds=500.0)
        sessions = get_practice_sessions(limit=10)
        assert len(sessions) == 3
        # Most recent first
        assert sessions[0]["training_type"] == "co2"

    def test_limit(self, tmp_db):
        for i in range(5):
            save_practice_session(training_type="free", duration_seconds=float(i))
        sessions = get_practice_sessions(limit=3)
        assert len(sessions) == 3

    def test_incomplete_session(self, tmp_db):
        save_practice_session(
            training_type="o2",
            duration_seconds=300.0,
            rounds_completed=4,
            completed=False,
        )
        sessions = get_practice_sessions(limit=1)
        assert sessions[0]["completed"] == 0
        assert sessions[0]["rounds_completed"] == 4

    def test_get_by_id(self, tmp_db):
        save_practice_session(training_type="free", duration_seconds=45.0)
        save_practice_session(training_type="o2", duration_seconds=600.0)
        sessions = get_practice_sessions(limit=10)
        session_id = sessions[0]["id"]

        result = get_session_by_id(session_id)
        assert result is not None
        assert result["id"] == session_id

    def test_get_by_id_not_found(self, tmp_db):
        result = get_session_by_id(99999)
        assert result is None


class TestContractions:
    def test_save_and_count(self, tmp_db):
        save_practice_session(training_type="free", duration_seconds=90.0)
        sessions = get_practice_sessions(limit=1)
        session_id = sessions[0]["id"]

        save_contraction(session_id, 45.2)
        save_contraction(session_id, 62.8)
        save_contraction(session_id, 78.1)

        count = get_contraction_count_for_session(session_id)
        assert count == 3

    def test_get_contractions_with_timestamps(self, tmp_db):
        save_practice_session(training_type="free", duration_seconds=90.0)
        sessions = get_practice_sessions(limit=1)
        session_id = sessions[0]["id"]

        save_contraction(session_id, 45.2)
        save_contraction(session_id, 62.8)

        contractions = get_contractions_for_session(session_id)
        assert len(contractions) == 2
        assert contractions[0]["seconds_into_hold"] == 45.2
        assert contractions[1]["seconds_into_hold"] == 62.8

    def test_no_contractions(self, tmp_db):
        save_practice_session(training_type="free", duration_seconds=90.0)
        sessions = get_practice_sessions(limit=1)
        session_id = sessions[0]["id"]

        count = get_contraction_count_for_session(session_id)
        assert count == 0

        contractions = get_contractions_for_session(session_id)
        assert contractions == []


class TestBestFreeDuration:
    def test_no_sessions(self, tmp_db):
        assert get_best_free_duration() is None

    def test_single_session(self, tmp_db):
        save_practice_session(
            training_type="free", duration_seconds=90.0, completed=True
        )
        assert get_best_free_duration() == 90.0

    def test_multiple_sessions(self, tmp_db):
        save_practice_session(
            training_type="free", duration_seconds=60.0, completed=True
        )
        save_practice_session(
            training_type="free", duration_seconds=120.0, completed=True
        )
        save_practice_session(
            training_type="free", duration_seconds=90.0, completed=True
        )
        assert get_best_free_duration() == 120.0

    def test_ignores_incomplete(self, tmp_db):
        save_practice_session(
            training_type="free", duration_seconds=200.0, completed=False
        )
        save_practice_session(
            training_type="free", duration_seconds=90.0, completed=True
        )
        assert get_best_free_duration() == 90.0

    def test_ignores_non_free(self, tmp_db):
        save_practice_session(
            training_type="o2", duration_seconds=600.0, completed=True
        )
        assert get_best_free_duration() is None


class TestScores:
    def test_save_and_get_best(self, tmp_db):
        save_score("free", 90.0)
        save_score("free", 120.0)
        save_score("free", 80.0)

        from apno.utils.database import get_best_score

        best = get_best_score("free")
        assert best == 120.0

    def test_no_scores(self, tmp_db):
        from apno.utils.database import get_best_score

        assert get_best_score("free") is None


class TestTrainingTypesByDate:
    def test_returns_types_for_today(self, tmp_db):
        save_practice_session(training_type="free", duration_seconds=90.0)
        save_practice_session(training_type="o2", duration_seconds=600.0)

        result = get_training_types_by_date(days=1)
        # Should have at least today's date with both types
        assert len(result) >= 1
        for types in result.values():
            assert "free" in types or "o2" in types


class TestSettings:
    def test_save_and_load(self, tmp_db):
        save_settings({"key1": "value1", "key2": "value2"})
        loaded = load_settings()
        assert loaded["key1"] == "value1"
        assert loaded["key2"] == "value2"

    def test_overwrite(self, tmp_db):
        save_settings({"key1": "old"})
        save_settings({"key1": "new"})
        loaded = load_settings()
        assert loaded["key1"] == "new"

    def test_empty(self, tmp_db):
        loaded = load_settings()
        assert loaded == {}

    def test_multiple_saves_preserve_other_keys(self, tmp_db):
        save_settings({"a": "1", "b": "2"})
        save_settings({"b": "3", "c": "4"})
        loaded = load_settings()
        assert loaded["a"] == "1"
        assert loaded["b"] == "3"
        assert loaded["c"] == "4"
