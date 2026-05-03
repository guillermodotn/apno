"""Screen utilities for wake-lock and settings access."""

from kivy.core.window import Window


def set_keep_screen_on(enabled: bool) -> None:
    """Enable or disable the screen wake-lock.

    When enabled, prevents the device screen from turning off.
    Uses Kivy's Window.allow_screensaver which maps to
    FLAG_KEEP_SCREEN_ON on Android.

    Args:
        enabled: True to keep screen on, False to allow screen sleep.
    """
    Window.allow_screensaver = not enabled


def is_keep_screen_on() -> bool:
    """Check if the keep_screen_on setting is enabled."""
    from kivy.app import App

    app = App.get_running_app()
    if app and app.root:
        try:
            settings = app.root.ids.screen_manager.get_screen("settings")
            return settings.keep_screen_on
        except Exception:
            pass
    return True
