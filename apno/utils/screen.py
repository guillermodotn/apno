"""Screen wake-lock utility for keeping the display on during training."""

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
