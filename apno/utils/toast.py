"""Toast notification utility for showing brief messages."""

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.label import Label
from kivy.uix.widget import Widget


def show_toast(message: str, duration: int = 3) -> None:
    """Show a toast notification at the bottom of the screen.

    Displays a dark rounded pill with white text that fades in,
    holds for the specified duration, then fades out and removes itself.

    Args:
        message: The text to display.
        duration: How long to show the toast in seconds.
    """
    app = App.get_running_app()
    root = app.root if app else None
    if not root:
        return

    toast = Widget(
        size_hint=(None, None),
        size=(dp(300), dp(44)),
        opacity=0,
    )

    with toast.canvas:
        Color(0.2, 0.2, 0.2, 0.9)
        bg_rect = RoundedRectangle(pos=toast.pos, size=toast.size, radius=[dp(22)])

    toast.bind(
        pos=lambda w, p: setattr(bg_rect, "pos", p),
        size=lambda w, s: setattr(bg_rect, "size", s),
    )

    label = Label(
        text=message,
        font_size=sp(14),
        color=(1, 1, 1, 1),
        size=toast.size,
        pos=toast.pos,
    )
    toast.bind(
        pos=lambda w, p: setattr(label, "pos", p),
        size=lambda w, s: setattr(label, "size", s),
    )
    toast.add_widget(label)

    root.add_widget(toast)

    def position(*_args):
        toast.x = (root.width - toast.width) / 2
        toast.y = dp(24)

    Clock.schedule_once(position, 0)

    anim = (
        Animation(opacity=1, duration=0.2)
        + Animation(duration=duration)
        + Animation(opacity=0, duration=0.3)
    )
    anim.bind(on_complete=lambda *a: root.remove_widget(toast))
    anim.start(toast)
