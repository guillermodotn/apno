from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.widget import Widget


class ProgressCircle(Widget):
    """A circular progress indicator with smooth animations."""

    progress = NumericProperty(0)  # Progress percentage (0 to 100)
    progress_color = ListProperty([0.15, 0.40, 0.65, 1])  # Deep Ocean Blue
    line_width = NumericProperty(8)
    background_color = ListProperty([0.9, 0.9, 0.9, 1])  # Light grey
    overlay_progress = NumericProperty(0)  # Second ring progress (0 to 100)
    overlay_color = ListProperty([0.85, 0.65, 0.1, 1])  # Gold

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(progress=self.update_canvas)
        self.bind(progress_color=self.update_canvas)
        self.bind(overlay_progress=self.update_canvas)
        self.bind(overlay_color=self.update_canvas)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        # Schedule initial draw after layout is complete
        Clock.schedule_once(self._initial_draw, 0)

    def _initial_draw(self, dt):
        """Draw after the first frame when layout is ready."""
        self.update_canvas()

    def update_canvas(self, *args):
        """Redraw the progress circle."""
        # Skip if size is not yet determined
        if self.width <= 1 or self.height <= 1:
            return

        self.canvas.clear()

        radius = min(self.width, self.height) / 2 - self.line_width - 5
        if radius <= 0:
            return

        with self.canvas:
            # Background circle
            Color(*self.background_color)
            Line(
                circle=(self.center_x, self.center_y, radius),
                width=self.line_width / 2,
            )

            # Progress arc
            if self.progress > 0:
                Color(*self.progress_color)
                # Draw from top (90 degrees) going clockwise
                angle = 360 * self.progress / 100
                Line(
                    circle=(self.center_x, self.center_y, radius, 90, 90 - angle),
                    width=self.line_width,
                    cap="round",
                )

            # Overlay arc (second ring drawn on top)
            if self.overlay_progress > 0:
                Color(*self.overlay_color)
                overlay_angle = 360 * self.overlay_progress / 100
                Line(
                    circle=(
                        self.center_x,
                        self.center_y,
                        radius,
                        90,
                        90 - overlay_angle,
                    ),
                    width=self.line_width,
                    cap="round",
                )

    def on_size(self, *args):
        """Redraw when widget size changes."""
        self.update_canvas()

    def set_progress(self, value, duration=0.5):
        """Smoothly animate progress to the desired value."""
        value = max(0, min(100, value))
        Animation(progress=value, duration=duration, t="out_quad").start(self)

    def set_overlay(self, value, duration=0.5):
        """Smoothly animate overlay progress to the desired value."""
        value = max(0, min(100, value))
        Animation(overlay_progress=value, duration=duration, t="out_quad").start(self)

    def reset(self):
        """Reset progress to zero."""
        self.set_progress(0, duration=0.3)
