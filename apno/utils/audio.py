"""Sound playback utility for training audio feedback."""

import os

from kivy.app import App
from kivy.core.audio import SoundLoader

_sounds: dict = {}

SOUND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "assets", "sounds"
)

SOUND_NAMES = [
    "countdown_tick",
    "hold_start",
    "rest_start",
    "session_complete",
    "contraction_tap",
]


def load_sounds() -> None:
    """Preload all sound files. Call once at app startup."""
    for name in SOUND_NAMES:
        path = os.path.join(SOUND_DIR, f"{name}.wav")
        sound = SoundLoader.load(path)
        if sound:
            _sounds[name] = sound


def _is_sound_enabled() -> bool:
    """Check if the sound setting is enabled."""
    app = App.get_running_app()
    if app and app.root:
        try:
            settings = app.root.ids.screen_manager.get_screen("settings")
            return settings.sound_enabled
        except Exception:
            pass
    return True


def play(name: str) -> None:
    """Play a sound by name if sound is enabled.

    Args:
        name: One of 'countdown_tick', 'hold_start', 'rest_start',
              'session_complete', 'contraction_tap'.
    """
    if not _is_sound_enabled():
        return
    sound = _sounds.get(name)
    if sound:
        sound.stop()
        sound.play()
