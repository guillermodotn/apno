"""Shared test fixtures."""

import sys
from types import ModuleType

import pytest

# Minimal kivy.utils mock so app modules can import without Kivy installed.
# Only mocks kivy.utils.platform — the single attribute used at module level.
# When Kivy is installed (local dev), the real module is used instead.
if "kivy" not in sys.modules:
    kivy_mock = ModuleType("kivy")
    kivy_utils_mock = ModuleType("kivy.utils")
    kivy_utils_mock.platform = "linux"
    sys.modules["kivy"] = kivy_mock
    sys.modules["kivy.utils"] = kivy_utils_mock


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Create a temporary database for testing."""
    from apno.utils import database

    monkeypatch.setattr(database, "get_data_dir", lambda: tmp_path)
    database.init_db()
    yield tmp_path / "apno.db"
