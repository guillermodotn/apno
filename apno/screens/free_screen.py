from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

from apno.utils.database import (
    get_best_score,
    save_contraction,
    save_practice_session,
    save_score,
)
from apno.utils.screen import set_keep_screen_on

Builder.load_string("""
#:import ProgressCircle apno.widgets.progress_circle.ProgressCircle
#:import StyledButton apno.widgets.styled_button.StyledButton
#:import OutlinedButton apno.widgets.styled_button.OutlinedButton

<FreeScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(8)

        # Session info
        Label:
            text: f"Hold #{root.hold_count}" if root.hold_count > 0 else "Free Training"
            font_size: sp(16)
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: dp(28)

        # Phase indicator
        Label:
            text: root.phase_text
            font_size: sp(28)
            bold: True
            color: root.phase_color
            size_hint_y: None
            height: dp(44)

        RelativeLayout:
            id: chrono_area
            size_hint_y: 1

            ProgressCircle:
                id: progress_circle
                size_hint: None, None
                size: min(self.parent.width, self.parent.height) * 0.7, min(self.parent.width, self.parent.height) * 0.7
                pos: (self.parent.width - self.width) / 2, (self.parent.height - self.height) / 2
                progress_color: root.phase_color

            Label:
                text: root.time_text
                font_size: sp(56)
                bold: True
                color: 0.1, 0.1, 0.1, 1
                size_hint: None, None
                size: dp(200), dp(80)
                pos: (self.parent.width - self.width) / 2, (self.parent.height - self.height) / 2

        # Contraction counter
        Label:
            text: f"Contractions: {root.contraction_count}" if root.is_holding else ""
            font_size: sp(16)
            color: 0.9, 0.5, 0.2, 1
            size_hint_y: None
            height: dp(32)
            opacity: 1 if root.is_holding else 0

        # Best time display
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(24)
            spacing: dp(24)
            padding: dp(16), 0

            Label:
                text: root.best_time_text
                font_size: sp(16)
                bold: True
                color: 0.3, 0.3, 0.3, 1

            Label:
                text: root.alltime_best_text
                font_size: sp(16)
                bold: True
                color: 0.2, 0.6, 0.4, 1

        # Instruction text
        Label:
            text: root.instruction_text
            font_size: sp(15)
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: dp(36)
            text_size: self.width, None
            halign: "center"

        # Control buttons
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: dp(56)
            spacing: dp(16)
            padding: dp(16), 0

            OutlinedButton:
                text: "Reset"
                size_hint_x: 0.5
                on_release: root.reset_session()

            StyledButton:
                text: root.button_text
                size_hint_x: 0.5
                on_release: root.toggle_hold()
""")  # noqa E501


class FreeScreen(Screen):
    """Free Training: Practice breath holds at your own pace with a timer."""

    time_text = StringProperty("00:00")
    phase_text = StringProperty("Ready")
    instruction_text = StringProperty("Tap Start when you're ready to hold")
    best_time_text = StringProperty("Session: --:--")
    alltime_best_text = StringProperty("All-time: --:--")
    button_text = StringProperty("Start Hold")
    phase_color = [0.4, 0.4, 0.8, 1]

    hold_count = NumericProperty(0)
    is_holding = BooleanProperty(False)
    elapsed_time = NumericProperty(0)
    best_time = NumericProperty(0)
    alltime_best = NumericProperty(0)
    contraction_count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer_event = None
        self.phase = "ready"  # ready, hold
        self._update_phase_color()
        self._load_alltime_best()
        self.contractions = []
        self.session_id = None

    def _is_keep_screen_on(self):
        """Check if keep_screen_on setting is enabled."""
        app = App.get_running_app()
        if app and app.root:
            try:
                settings = app.root.ids.screen_manager.get_screen("settings")
                return settings.keep_screen_on
            except Exception:
                pass
        return True

    def on_enter(self):
        """Called when screen is entered."""
        self._load_alltime_best()
        self._reset_display()
        if self._is_keep_screen_on():
            set_keep_screen_on(True)

    def on_leave(self):
        """Called when leaving the screen."""
        self._stop_timer()
        set_keep_screen_on(False)

    def on_touch_down(self, touch):
        """Handle touch events - record contraction when tapping timer during hold."""
        if self.is_holding and self.ids.chrono_area.collide_point(*touch.pos):
            self.record_contraction()
            return True
        return super().on_touch_down(touch)

    def _reset_display(self):
        """Reset display without clearing best time."""
        self.phase = "ready"
        self.is_holding = False
        self.elapsed_time = 0
        self.time_text = "00:00"
        self.phase_text = "Ready"
        self.instruction_text = "Tap Start when you're ready to hold"
        self.button_text = "Start Hold"
        self._update_phase_color()
        if hasattr(self, "ids") and "progress_circle" in self.ids:
            self.ids.progress_circle.set_progress(0, duration=0.3)

    def reset_session(self):
        """Full reset including hold count and session best time."""
        self._stop_timer()
        self.hold_count = 0
        self.best_time = 0
        self.best_time_text = "Session: --:--"
        self.contractions = []
        self.contraction_count = 0
        self.session_id = None
        self._reset_display()

    def _load_alltime_best(self):
        """Load the all-time best from the database."""
        best = get_best_score("free")
        if best is not None:
            self.alltime_best = best
            self._update_alltime_best_display()
        else:
            self.alltime_best = 0
            self.alltime_best_text = "All-time: --:--"

    def toggle_hold(self):
        """Start or stop a breath hold."""
        if self.is_holding:
            self._end_hold()
        else:
            self._start_hold()

    def _start_hold(self):
        """Begin a breath hold."""
        self.phase = "hold"
        self.is_holding = True
        self.elapsed_time = 0
        self.hold_count += 1
        self.contractions = []
        self.contraction_count = 0
        self.session_id = None
        self.phase_text = "Holding..."
        self.instruction_text = "Tap anywhere on the timer when you feel a contraction"
        self.button_text = "Stop"
        self._update_phase_color()
        self.timer_event = Clock.schedule_interval(self._update_timer, 0.1)

    def record_contraction(self):
        """Record a contraction during the current hold."""
        if not self.is_holding:
            return
        self.contractions.append(self.elapsed_time)
        self.contraction_count = len(self.contractions)

    def _end_hold(self):
        """End the current breath hold."""
        self._stop_timer()
        self.phase = "ready"
        self.is_holding = False

        is_new_session_best = self.elapsed_time > self.best_time
        is_new_alltime_best = self.elapsed_time > self.alltime_best

        # Save the practice session for this hold
        self.session_id = save_practice_session(
            training_type="free",
            duration_seconds=self.elapsed_time,
            rounds_completed=1,
            parameters={
                "hold_number": self.hold_count,
                "hold_time": self.elapsed_time,
                "is_session_best": is_new_session_best,
                "is_alltime_best": is_new_alltime_best,
                "contraction_count": len(self.contractions),
            },
            completed=True,
        )

        # Save contractions if any were recorded
        for contraction_time in self.contractions:
            save_contraction(self.session_id, contraction_time)

        # Check for new session best time
        if is_new_session_best:
            self.best_time = self.elapsed_time
            self._update_best_time_display()

        # Check for new all-time best
        if is_new_alltime_best:
            self.alltime_best = self.elapsed_time
            save_score("free", self.elapsed_time)
            self._update_alltime_best_display()
            self.phase_text = "New All-Time Best!"
            self.instruction_text = "Amazing! You've set a new personal record!"
        elif is_new_session_best:
            self.phase_text = "New Session Best!"
            self.instruction_text = "Great job! Take recovery breaths"
        else:
            self.phase_text = "Done"
            contraction_summary = (
                f" ({len(self.contractions)} contractions)" if self.contractions else ""
            )
            self.instruction_text = (
                f"Good effort!{contraction_summary} Recover and try again"
            )

        self.button_text = "Start Hold"
        self._update_phase_color()

        # Keep progress at 100% briefly to show completion
        if hasattr(self, "ids") and "progress_circle" in self.ids:
            self.ids.progress_circle.set_progress(100, duration=0.3)

    def _stop_timer(self):
        """Stop the timer if running."""
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None

    def _update_timer(self, dt):
        """Update the timer display."""
        self.elapsed_time += dt
        self._update_time_display()
        self._update_progress()
        self._update_phase_color()

    def _update_time_display(self):
        """Update the time display."""
        total_seconds = int(self.elapsed_time)
        mins, secs = divmod(total_seconds, 60)
        # Show tenths of a second for more precise timing
        tenths = int((self.elapsed_time - total_seconds) * 10)
        if mins > 0:
            self.time_text = f"{mins:02}:{secs:02}"
        else:
            self.time_text = f"{secs:02}.{tenths}"

    def _update_best_time_display(self):
        """Update the session best time display."""
        total_seconds = int(self.best_time)
        mins, secs = divmod(total_seconds, 60)
        self.best_time_text = f"Session: {mins:02}:{secs:02}"

    def _update_alltime_best_display(self):
        """Update the all-time best display."""
        total_seconds = int(self.alltime_best)
        mins, secs = divmod(total_seconds, 60)
        self.alltime_best_text = f"All-time: {mins:02}:{secs:02}"

    def _update_progress(self):
        """Update progress circle based on elapsed time."""
        if not hasattr(self, "ids") or "progress_circle" not in self.ids:
            return

        # Progress based on a 3-minute target (180 seconds)
        target_time = 180
        progress = min(100, (self.elapsed_time / target_time) * 100)
        self.ids.progress_circle.set_progress(progress, duration=0.1)

    def _update_phase_color(self):
        """Update the color based on current phase."""
        if self.phase == "hold":
            # Change color based on elapsed time
            if self.elapsed_time < 30:
                self.phase_color = [0.2, 0.7, 0.4, 1]  # Green - easy
            elif self.elapsed_time < 60:
                self.phase_color = [0.9, 0.7, 0.2, 1]  # Yellow - moderate
            elif self.elapsed_time < 90:
                self.phase_color = [0.9, 0.5, 0.2, 1]  # Orange - challenging
            else:
                self.phase_color = [0.9, 0.3, 0.3, 1]  # Red - intense
        else:
            self.phase_color = [0.4, 0.4, 0.8, 1]  # Purple - ready
