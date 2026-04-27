import os

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from apno.utils.database import get_best_score, load_settings, save_settings
from apno.utils.export import export_sessions_json

Builder.load_string("""
#:import StyledCard apno.widgets.styled_card.StyledCard
#:import OutlinedButton apno.widgets.styled_button.OutlinedButton
#:import RoundedRectangle kivy.graphics.RoundedRectangle


<SettingStepper@BoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(48)
    padding: 0, dp(4)
    spacing: dp(12)
    setting_label: ""
    setting_value: 60
    step_value: 15
    min_value: 15
    max_value: 300
    accent_color: 0.15, 0.40, 0.65, 1
    locked: False

    Label:
        text: root.setting_label
        font_size: sp(14)
        color: (0.6, 0.6, 0.6, 1) if root.locked else (0.2, 0.2, 0.2, 1)
        text_size: self.size
        halign: "left"
        valign: "middle"
        size_hint_x: 0.45

    BoxLayout:
        size_hint_x: 0.55
        spacing: dp(8)
        padding: 0

        Button:
            text: "-"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: (0.96, 0.96, 0.96, 1) if root.locked else (0.92, 0.92, 0.92, 1)
            color: (0.7, 0.7, 0.7, 1) if root.locked else (0.3, 0.3, 0.3, 1)
            on_release: root.setting_value = root.setting_value if root.locked else max(root.min_value, root.setting_value - root.step_value)

        Label:
            text: f"{int(root.setting_value // 60)}:{int(root.setting_value % 60):02d}"
            font_size: sp(16)
            bold: True
            color: (0.7, 0.7, 0.7, 1) if root.locked else root.accent_color
            size_hint_x: None
            width: dp(50)
            halign: "center"

        Button:
            text: "+"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: (0.96, 0.96, 0.96, 1) if root.locked else (0.92, 0.92, 0.92, 1)
            color: (0.7, 0.7, 0.7, 1) if root.locked else (0.3, 0.3, 0.3, 1)
            on_release: root.setting_value = root.setting_value if root.locked else min(root.max_value, root.setting_value + root.step_value)


<RoundsStepper@BoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(48)
    padding: 0, dp(4)
    spacing: dp(12)
    rounds_value: 8
    min_rounds: 4
    max_rounds: 12
    accent_color: 0.15, 0.40, 0.65, 1
    locked: False

    Label:
        text: "Rounds"
        font_size: sp(14)
        color: (0.6, 0.6, 0.6, 1) if root.locked else (0.2, 0.2, 0.2, 1)
        text_size: self.size
        halign: "left"
        valign: "middle"
        size_hint_x: 0.45

    BoxLayout:
        size_hint_x: 0.55
        spacing: dp(8)
        padding: 0

        Button:
            text: "-"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: (0.96, 0.96, 0.96, 1) if root.locked else (0.92, 0.92, 0.92, 1)
            color: (0.7, 0.7, 0.7, 1) if root.locked else (0.3, 0.3, 0.3, 1)
            on_release: root.rounds_value = root.rounds_value if root.locked else max(root.min_rounds, root.rounds_value - 1)

        Label:
            text: str(int(root.rounds_value))
            font_size: sp(16)
            bold: True
            color: (0.7, 0.7, 0.7, 1) if root.locked else root.accent_color
            size_hint_x: None
            width: dp(50)
            halign: "center"

        Button:
            text: "+"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: (0.96, 0.96, 0.96, 1) if root.locked else (0.92, 0.92, 0.92, 1)
            color: (0.7, 0.7, 0.7, 1) if root.locked else (0.3, 0.3, 0.3, 1)
            on_release: root.rounds_value = root.rounds_value if root.locked else min(root.max_rounds, root.rounds_value + 1)


<SectionHeader@BoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(32)
    spacing: dp(8)
    header_text: ""
    accent_color: 0.15, 0.40, 0.65, 1

    Widget:
        size_hint: None, None
        size: dp(4), dp(20)
        pos_hint: {"center_y": 0.5}
        canvas:
            Color:
                rgba: root.accent_color
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [2]

    Label:
        text: root.header_text
        font_size: sp(16)
        bold: True
        color: root.accent_color
        text_size: self.size
        halign: "left"
        valign: "middle"


<Divider@Widget>:
    size_hint_y: None
    height: dp(1)
    canvas:
        Color:
            rgba: 0.9, 0.9, 0.9, 1
        Rectangle:
            pos: self.x + dp(16), self.y
            size: self.width - dp(32), self.height


<ToggleSwitch@Widget>:
    active: False
    active_color: 0.15, 0.40, 0.65, 1
    size_hint: None, None
    size: dp(48), dp(28)
    canvas:
        # Track
        Color:
            rgba: self.active_color if self.active else [0.75, 0.75, 0.75, 1]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
        # Knob
        Color:
            rgba: 1, 1, 1, 1
        Ellipse:
            pos: (self.x + self.width - dp(24)) if self.active else (self.x + dp(4)), self.y + dp(4)
            size: dp(20), dp(20)
    on_touch_down: self.active = not self.active if self.collide_point(*args[1].pos) else self.active


<SettingsScreen>:
    ScrollView:
        do_scroll_x: False
        bar_width: dp(4)

        BoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height

            # CO2 Table (internal: o2_screen — fixed hold, decreasing breathe)
            SectionHeader:
                header_text: "CO2 Table"
                accent_color: 1.0, 0.7, 0.2, 1

            StyledCard:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16), dp(16), dp(16), dp(8)
                spacing: 0

                SettingStepper:
                    setting_label: "Hold Time"
                    setting_value: root.o2_hold_time
                    min_value: 30
                    max_value: 300
                    step_value: 15
                    accent_color: 1.0, 0.7, 0.2, 1
                    locked: root.auto_configure
                    on_setting_value: root.update_o2_hold(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Initial Breathe"
                    setting_value: root.o2_initial_breathe
                    min_value: 30
                    max_value: 300
                    step_value: 15
                    accent_color: 1.0, 0.7, 0.2, 1
                    locked: root.auto_configure
                    on_setting_value: root.update_o2_breathe(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Breathe Decrement"
                    setting_value: root.o2_breathe_decrement
                    min_value: 5
                    max_value: 30
                    step_value: 5
                    accent_color: 1.0, 0.7, 0.2, 1
                    locked: root.auto_configure
                    on_setting_value: root.update_o2_breathe_decrement(self.setting_value)

                Divider:

                RoundsStepper:
                    rounds_value: root.o2_rounds
                    accent_color: 1.0, 0.7, 0.2, 1
                    locked: root.auto_configure
                    on_rounds_value: root.update_o2_rounds(self.rounds_value)

                Divider:

                BoxLayout:
                    size_hint_y: None
                    height: dp(40)
                    padding: 0

                    Label:
                        text: root.o2_summary
                        font_size: sp(13)
                        color: 0.5, 0.5, 0.5, 1
                        text_size: self.size
                        halign: "left"
                        valign: "middle"

            # O2 Table (internal: co2_screen — increasing hold, fixed breathe)
            SectionHeader:
                header_text: "O2 Table"
                accent_color: 0.25, 0.45, 0.85, 1

            StyledCard:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16), dp(16), dp(16), dp(8)
                spacing: 0

                SettingStepper:
                    setting_label: "Initial Hold"
                    setting_value: root.co2_initial_hold
                    min_value: 30
                    max_value: 180
                    step_value: 15
                    accent_color: 0.25, 0.45, 0.85, 1
                    locked: root.auto_configure
                    on_setting_value: root.update_co2_hold(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Hold Increment"
                    setting_value: root.co2_hold_increment
                    min_value: 5
                    max_value: 30
                    step_value: 5
                    accent_color: 0.25, 0.45, 0.85, 1
                    locked: root.auto_configure
                    on_setting_value: root.update_co2_increment(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Breathe Time"
                    setting_value: root.co2_breathe_time
                    min_value: 60
                    max_value: 300
                    step_value: 15
                    accent_color: 0.25, 0.45, 0.85, 1
                    locked: root.auto_configure
                    on_setting_value: root.update_co2_breathe(self.setting_value)

                Divider:

                RoundsStepper:
                    rounds_value: root.co2_rounds
                    accent_color: 0.25, 0.45, 0.85, 1
                    locked: root.auto_configure
                    on_rounds_value: root.update_co2_rounds(self.rounds_value)

                Divider:

                BoxLayout:
                    size_hint_y: None
                    height: dp(40)
                    padding: 0

                    Label:
                        text: root.co2_summary
                        font_size: sp(13)
                        color: 0.5, 0.5, 0.5, 1
                        text_size: self.size
                        halign: "left"
                        valign: "middle"

            # General Section
            SectionHeader:
                header_text: "General"
                accent_color: 0.15, 0.40, 0.65, 1

            StyledCard:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16), dp(12)
                spacing: 0

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: dp(56)

                    BoxLayout:
                        orientation: "vertical"
                        spacing: dp(2)

                        Label:
                            text: "Auto-configure tables"
                            font_size: sp(14)
                            color: 0.2, 0.2, 0.2, 1
                            text_size: self.size
                            halign: "left"
                            valign: "bottom"
                            size_hint_y: 0.5

                        Label:
                            text: root.personal_best_text
                            font_size: sp(12)
                            color: 0.5, 0.5, 0.5, 1
                            text_size: self.size
                            halign: "left"
                            valign: "top"
                            size_hint_y: 0.5

                    ToggleSwitch:
                        active: root.auto_configure
                        on_active: root.auto_configure = self.active
                        pos_hint: {"center_y": 0.5}
                        active_color: 0.15, 0.40, 0.65, 1

                Divider:

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: dp(48)

                    Label:
                        text: "Keep screen on"
                        font_size: sp(14)
                        color: 0.2, 0.2, 0.2, 1
                        text_size: self.size
                        halign: "left"
                        valign: "middle"

                    ToggleSwitch:
                        active: root.keep_screen_on
                        on_active: root.keep_screen_on = self.active
                        pos_hint: {"center_y": 0.5}
                        active_color: 0.15, 0.40, 0.65, 1

                Divider:

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: dp(48)

                    Label:
                        text: "Sound"
                        font_size: sp(14)
                        color: 0.2, 0.2, 0.2, 1
                        text_size: self.size
                        halign: "left"
                        valign: "middle"

                    ToggleSwitch:
                        active: root.sound_enabled
                        on_active: root.sound_enabled = self.active
                        pos_hint: {"center_y": 0.5}
                        active_color: 0.15, 0.40, 0.65, 1

            # Export and Reset Buttons
            OutlinedButton:
                text: "Export Data"
                size_hint_y: None
                height: dp(44)
                on_release: root.export_data()

            OutlinedButton:
                text: "Reset to Defaults"
                size_hint_y: None
                height: dp(44)
                on_release: root.reset_defaults()

            Widget:
                size_hint_y: None
                height: dp(16)
""")  # noqa E501


class SettingsScreen(Screen):
    # O2 Table settings
    o2_hold_time = NumericProperty(60)  # 1 minute
    o2_initial_breathe = NumericProperty(120)  # 2 minutes
    o2_breathe_decrement = NumericProperty(10)  # 10 seconds
    o2_rounds = NumericProperty(8)

    # CO2 Table settings
    co2_initial_hold = NumericProperty(30)  # 30 seconds
    co2_hold_increment = NumericProperty(10)  # 10 seconds
    co2_breathe_time = NumericProperty(120)  # 2 minutes
    co2_rounds = NumericProperty(6)

    # General settings
    auto_configure = BooleanProperty(False)
    keep_screen_on = BooleanProperty(True)
    sound_enabled = BooleanProperty(True)
    personal_best_text = StringProperty("No personal best yet")

    # Summaries
    o2_summary = StringProperty("")
    co2_summary = StringProperty("")

    # Setting keys for database persistence
    _setting_keys = {
        "o2_hold_time": float,
        "o2_initial_breathe": float,
        "o2_breathe_decrement": float,
        "o2_rounds": float,
        "co2_initial_hold": float,
        "co2_hold_increment": float,
        "co2_breathe_time": float,
        "co2_rounds": float,
        "auto_configure": lambda v: v == "True",
        "keep_screen_on": lambda v: v == "True",
        "sound_enabled": lambda v: v == "True",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loading = True
        self._load_from_db()
        self._loading = False
        self._update_personal_best_text()
        if self.auto_configure:
            self._auto_configure_from_best()
        self._update_summaries()
        # Apply settings after all screens are created
        Clock.schedule_once(lambda dt: self._apply_settings(), 0)

    def on_enter(self, *args):
        """Refresh personal best and recalculate if auto-configure is on."""
        self._update_personal_best_text()
        if self.auto_configure:
            self._auto_configure_from_best()

    def on_leave(self):
        """Re-apply settings when leaving the settings screen."""
        self._apply_settings()

    def on_keep_screen_on(self, instance, value):
        """Auto-save when keep_screen_on changes."""
        self._save_to_db()

    def on_sound_enabled(self, instance, value):
        """Auto-save when sound_enabled changes."""
        self._save_to_db()

    def on_auto_configure(self, instance, value):
        """Recalculate table parameters when auto-configure changes."""
        if value:
            self._auto_configure_from_best()
        self._save_to_db()

    def _update_personal_best_text(self):
        """Update the personal best display text."""
        best = get_best_score("free")
        if best and best > 0:
            mins, secs = divmod(int(best), 60)
            self.personal_best_text = f"Based on best: {mins}:{secs:02d}"
        else:
            self.personal_best_text = "No personal best yet"

    def _round_to_5(self, value):
        """Round a value to the nearest 5 seconds."""
        return max(5, round(value / 5) * 5)

    def _auto_configure_from_best(self):
        """Calculate O2/CO2 table parameters from personal best hold."""
        best = get_best_score("free")
        if not best or best <= 0:
            return

        # CO2 Table (internal: o2) — fixed hold at 50%, decreasing breathe
        self.o2_hold_time = self._round_to_5(best * 0.5)
        self.o2_initial_breathe = 120  # Standard 2 minutes
        self.o2_breathe_decrement = 15  # Standard 15s decrement
        self.o2_rounds = 8

        # O2 Table (internal: co2) — increasing hold from 30%, fixed breathe
        initial = self._round_to_5(best * 0.3)
        self.co2_initial_hold = initial
        self.co2_hold_increment = self._round_to_5((best - initial) / 7)
        self.co2_breathe_time = 120  # Standard 2 minutes
        self.co2_rounds = 8

        self._update_summaries()
        self._apply_settings()

    def _format_time(self, seconds):
        """Format seconds as M:SS."""
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}:{secs:02d}"

    def _update_summaries(self):
        """Update the training summary text."""
        # CO2 table summary (internal: o2): fixed hold, decreasing breathe
        final_breathe = max(
            15,
            self.o2_initial_breathe - (self.o2_rounds - 1) * self.o2_breathe_decrement,
        )
        self.o2_summary = (
            f"{int(self.o2_rounds)} rounds: "
            f"{self._format_time(self.o2_hold_time)} hold, "
            f"breathe {self._format_time(self.o2_initial_breathe)} to {self._format_time(final_breathe)}"  # noqa E501
        )

        # O2 table summary (internal: co2): increasing hold, fixed breathe
        final_hold = (
            self.co2_initial_hold + (self.co2_rounds - 1) * self.co2_hold_increment
        )
        self.co2_summary = (
            f"{int(self.co2_rounds)} rounds: hold {self._format_time(self.co2_initial_hold)} to "  # noqa E501
            f"{self._format_time(final_hold)}, {self._format_time(self.co2_breathe_time)} breathe"  # noqa E501
        )

    def update_o2_hold(self, value):
        self.o2_hold_time = value
        self._update_summaries()
        self._apply_settings()

    def update_o2_breathe(self, value):
        self.o2_initial_breathe = value
        self._update_summaries()
        self._apply_settings()

    def update_o2_breathe_decrement(self, value):
        self.o2_breathe_decrement = value
        self._update_summaries()
        self._apply_settings()

    def update_o2_rounds(self, value):
        self.o2_rounds = value
        self._update_summaries()
        self._apply_settings()

    def update_co2_hold(self, value):
        self.co2_initial_hold = value
        self._update_summaries()
        self._apply_settings()

    def update_co2_increment(self, value):
        self.co2_hold_increment = value
        self._update_summaries()
        self._apply_settings()

    def update_co2_breathe(self, value):
        self.co2_breathe_time = value
        self._update_summaries()
        self._apply_settings()

    def update_co2_rounds(self, value):
        self.co2_rounds = value
        self._update_summaries()
        self._apply_settings()

    def _show_toast(self, message, duration=3):
        """Show a toast notification at the bottom of the screen."""
        app = App.get_running_app()
        root = app.root
        if not root:
            return

        # Use a plain Widget with canvas drawing — no Label to avoid
        # texture_update loops
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

        # Add text label as child
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

        # Position after layout
        def position(*_args):
            toast.x = (root.width - toast.width) / 2
            toast.y = dp(24)

        Clock.schedule_once(position, 0)

        # Fade in, hold, fade out, remove
        anim = (
            Animation(opacity=1, duration=0.2)
            + Animation(duration=duration)
            + Animation(opacity=0, duration=0.3)
        )
        anim.bind(on_complete=lambda *a: root.remove_widget(toast))
        anim.start(toast)

    def export_data(self):
        """Export all training data to JSON."""
        filepath = export_sessions_json()
        if not filepath:
            self._show_toast("No training sessions to export")
            return

        export_dir = "current directory" if os.environ.get("APNO_DEV") else "Downloads"
        self._show_toast(f"Data exported to {export_dir}")

    def reset_defaults(self):
        """Reset all settings to defaults."""
        self.o2_hold_time = 60
        self.o2_initial_breathe = 120
        self.o2_breathe_decrement = 10
        self.o2_rounds = 8
        self.co2_initial_hold = 30
        self.co2_hold_increment = 10
        self.co2_breathe_time = 120
        self.co2_rounds = 6
        self.auto_configure = False
        self.keep_screen_on = True
        self.sound_enabled = True
        self._update_summaries()
        self._apply_settings()

    def _load_from_db(self):
        """Load saved settings from the database."""
        try:
            saved = load_settings()
            for key, converter in self._setting_keys.items():
                if key in saved:
                    setattr(self, key, converter(saved[key]))
        except Exception:
            pass  # Use defaults if loading fails

    def _save_to_db(self):
        """Save current settings to the database."""
        if self._loading:
            return
        try:
            settings = {key: str(getattr(self, key)) for key in self._setting_keys}
            save_settings(settings)
        except Exception:
            pass  # Silently fail on save errors

    def _apply_settings(self):
        """Apply settings to the training screens and persist to database."""
        self._save_to_db()

        app = App.get_running_app()
        if not app or not app.root:
            return

        try:
            screen_manager = app.root.ids.screen_manager

            # Apply O2 settings
            o2_screen = screen_manager.get_screen("o2_screen")
            o2_screen.hold_time = int(self.o2_hold_time)
            o2_screen.initial_breathe_time = int(self.o2_initial_breathe)
            o2_screen.breathe_decrement = int(self.o2_breathe_decrement)
            o2_screen.total_rounds = int(self.o2_rounds)

            # Apply CO2 settings
            co2_screen = screen_manager.get_screen("co2_screen")
            co2_screen.initial_hold_time = int(self.co2_initial_hold)
            co2_screen.hold_increment = int(self.co2_hold_increment)
            co2_screen.breathe_time = int(self.co2_breathe_time)
            co2_screen.total_rounds = int(self.co2_rounds)
        except Exception:
            pass  # Settings will apply when screens are available
