from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.screenmanager import Screen

from apno.utils import audio
from apno.utils.database import save_practice_session
from apno.utils.screen import is_keep_screen_on, set_keep_screen_on

Builder.load_string("""
#:import ProgressCircle apno.widgets.progress_circle.ProgressCircle
#:import StyledButton apno.widgets.styled_button.StyledButton
#:import OutlinedButton apno.widgets.styled_button.OutlinedButton

<O2Screen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(8)

        # Round indicator
        Label:
            text: f"Round {root.current_round} of {root.total_rounds}"
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
                text: "Stop"
                size_hint_x: 0.5
                on_release: root.stop_training()

            StyledButton:
                text: "Pause" if root.is_running else "Start"
                size_hint_x: 0.5
                on_release: root.toggle_pause()
""")  # noqa E501


class O2Screen(Screen):
    """CO2 Table Training: Fixed hold time with decreasing breathe periods."""

    time_text = StringProperty("00:00")
    phase_text = StringProperty("Ready")
    instruction_text = StringProperty("Press Start to begin training")
    phase_color = ListProperty([1.0, 0.7, 0.2, 1])  # Amber (CO2 Table)

    current_round = NumericProperty(1)
    total_rounds = NumericProperty(8)
    is_running = BooleanProperty(False)

    # Training parameters (in seconds)
    hold_time = NumericProperty(60)  # 1 minute hold (fixed for O2)
    initial_breathe_time = NumericProperty(120)  # Starting breathe time
    breathe_decrement = NumericProperty(10)  # Decrease breathe by 10s each round

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_left = 0
        self.current_phase_duration = 0
        self.phase = "ready"  # ready, breathe, hold, complete
        self.timer_event = None
        self.session_start_time = None
        self._update_phase_color()

    def on_enter(self):
        """Called when screen is entered."""
        self.reset_training()
        if is_keep_screen_on():
            set_keep_screen_on(True)

    def on_leave(self):
        """Called when leaving the screen."""
        self.stop_training()
        set_keep_screen_on(False)

    def reset_training(self, save_incomplete: bool = False):
        """Reset training to initial state.

        Args:
            save_incomplete: If True, save an incomplete session record
        """
        # Save incomplete session if requested and training was in progress
        if (
            save_incomplete
            and self.session_start_time is not None
            and self.phase not in ("ready", "complete")
        ):
            duration = Clock.get_time() - self.session_start_time
            save_practice_session(
                training_type="o2",
                duration_seconds=duration,
                rounds_completed=self.current_round - 1,
                parameters={
                    "total_rounds": self.total_rounds,
                    "hold_time": self.hold_time,
                    "initial_breathe_time": self.initial_breathe_time,
                    "breathe_decrement": self.breathe_decrement,
                },
                completed=False,
            )

        self.current_round = 1
        self.phase = "ready"
        self.is_running = False
        self.time_left = 0
        self.time_text = "00:00"
        self.phase_text = "Ready"
        self.instruction_text = "Press Start to begin O2 table training"
        self.session_start_time = None
        self._update_phase_color()
        if hasattr(self, "ids") and "progress_circle" in self.ids:
            self.ids.progress_circle.set_progress(0, duration=0.3)

    def toggle_pause(self):
        """Start or pause the training."""
        if self.phase == "complete":
            self.reset_training()
            return

        if self.is_running:
            self.pause_training()
        else:
            self.start_training()

    def start_training(self):
        """Start or resume training."""
        self.is_running = True
        if self.phase == "ready":
            self.session_start_time = Clock.get_time()
            self._start_breathe_phase()
        if self.timer_event is None:
            self.timer_event = Clock.schedule_interval(self._update_timer, 1)

    def pause_training(self):
        """Pause the training."""
        self.is_running = False
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None

    def stop_training(self):
        """Stop and reset training."""
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
        self.reset_training(save_incomplete=True)

    def _start_breathe_phase(self):
        """Start the breathe phase (decreases each round)."""
        self.phase = "breathe"
        decrement = (self.current_round - 1) * self.breathe_decrement
        breathe_time = self.initial_breathe_time - decrement
        breathe_time = max(breathe_time, 15)  # Minimum 15 seconds
        self.time_left = breathe_time
        self.current_phase_duration = breathe_time
        self.phase_text = "Breathe"
        self.instruction_text = "Take deep, relaxed breaths"
        self._update_phase_color()
        self._update_display()

    def _start_hold_phase(self):
        """Start the breath-hold phase."""
        self.phase = "hold"
        self.time_left = self.hold_time
        self.current_phase_duration = self.hold_time
        self.phase_text = "Hold"
        self.instruction_text = "Hold your breath - stay relaxed"
        self._update_phase_color()
        self._update_display()

    def _complete_training(self):
        """Training session complete."""
        self.phase = "complete"
        self.is_running = False
        self.phase_text = "Complete!"
        self.instruction_text = "Great job! Training session finished."
        self.time_text = "--:--"
        self._update_phase_color()
        if self.timer_event:
            Clock.unschedule(self.timer_event)
            self.timer_event = None
        if hasattr(self, "ids") and "progress_circle" in self.ids:
            self.ids.progress_circle.set_progress(100, duration=0.5)

        # Save the practice session
        if self.session_start_time is not None:
            duration = Clock.get_time() - self.session_start_time
            save_practice_session(
                training_type="o2",
                duration_seconds=duration,
                rounds_completed=self.total_rounds,
                parameters={
                    "total_rounds": self.total_rounds,
                    "hold_time": self.hold_time,
                    "initial_breathe_time": self.initial_breathe_time,
                    "breathe_decrement": self.breathe_decrement,
                },
                completed=True,
            )
            self.session_start_time = None

    def _update_timer(self, dt):
        """Update the timer each second."""
        if not self.is_running:
            return

        if self.time_left > 0:
            self.time_left -= 1
            if self.time_left == 0:
                self._next_phase()
            else:
                # Countdown ticks in last 5 seconds of breathe phase
                if self.phase == "breathe" and self.time_left <= 5:
                    audio.play("countdown_tick")
                self._update_display()

    def _next_phase(self):
        """Transition to the next phase."""
        if self.phase == "breathe":
            audio.play("hold_start")
            self._start_hold_phase()
        elif self.phase == "hold":
            if self.current_round >= self.total_rounds:
                audio.play("session_complete")
                self._complete_training()
            else:
                self.current_round += 1
                audio.play("breathe_start")
                self._start_breathe_phase()

    def _update_display(self):
        """Update the timer display and progress."""
        mins, secs = divmod(self.time_left, 60)
        self.time_text = f"{mins:02}:{secs:02}"

        # Update progress circle
        if self.current_phase_duration > 0 and hasattr(self, "ids"):
            progress = (
                (self.current_phase_duration - self.time_left)
                / self.current_phase_duration
                * 100
            )
            if "progress_circle" in self.ids:
                self.ids.progress_circle.set_progress(progress, duration=0.3)

    def _update_phase_color(self):
        """Update the color based on current phase."""
        # Amber theme for CO2 table training
        colors = {
            "ready": [0.5, 0.5, 0.5, 1],
            "breathe": [0.2, 0.7, 0.4, 1],  # Green
            "hold": [1.0, 0.7, 0.2, 1],  # Amber (CO2 Table)
            "complete": [1.0, 0.7, 0.2, 1],  # Amber
        }
        self.phase_color = colors.get(self.phase, [0.5, 0.5, 0.5, 1])
