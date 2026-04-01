from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import Screen

from apno.utils.database import load_settings, save_settings

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

    Label:
        text: root.setting_label
        font_size: sp(14)
        color: 0.2, 0.2, 0.2, 1
        text_size: self.size
        halign: "left"
        valign: "middle"
        size_hint_x: 0.45

    BoxLayout:
        size_hint_x: 0.55
        spacing: dp(8)
        padding: 0

        Button:
            text: "−"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: 0.92, 0.92, 0.92, 1
            color: 0.3, 0.3, 0.3, 1
            on_release: root.setting_value = max(root.min_value, root.setting_value - root.step_value)

        Label:
            text: f"{int(root.setting_value // 60)}:{int(root.setting_value % 60):02d}"
            font_size: sp(16)
            bold: True
            color: root.accent_color
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
            background_color: 0.92, 0.92, 0.92, 1
            color: 0.3, 0.3, 0.3, 1
            on_release: root.setting_value = min(root.max_value, root.setting_value + root.step_value)


<RoundsStepper@BoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(48)
    rounds_value: 8
    min_rounds: 4
    max_rounds: 12
    accent_color: 0.15, 0.40, 0.65, 1

    Label:
        text: "Rounds"
        font_size: sp(14)
        color: 0.2, 0.2, 0.2, 1
        text_size: self.size
        halign: "left"
        valign: "middle"

    BoxLayout:
        size_hint_x: None
        width: dp(130)
        spacing: dp(12)

        Button:
            text: "−"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: 0.92, 0.92, 0.92, 1
            color: 0.3, 0.3, 0.3, 1
            on_release: root.rounds_value = max(root.min_rounds, root.rounds_value - 1)

        Label:
            text: str(int(root.rounds_value))
            font_size: sp(18)
            bold: True
            color: root.accent_color
            size_hint_x: None
            width: dp(30)
            halign: "center"

        Button:
            text: "+"
            font_size: sp(20)
            bold: True
            size_hint: None, None
            size: dp(36), dp(36)
            pos_hint: {"center_y": 0.5}
            background_normal: ""
            background_color: 0.92, 0.92, 0.92, 1
            color: 0.3, 0.3, 0.3, 1
            on_release: root.rounds_value = min(root.max_rounds, root.rounds_value + 1)


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

            # O2 Section
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
                    setting_label: "Hold Time"
                    setting_value: root.o2_hold_time
                    min_value: 30
                    max_value: 300
                    step_value: 15
                    accent_color: 0.25, 0.45, 0.85, 1
                    on_setting_value: root.update_o2_hold(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Initial Rest"
                    setting_value: root.o2_initial_rest
                    min_value: 30
                    max_value: 300
                    step_value: 15
                    accent_color: 0.25, 0.45, 0.85, 1
                    on_setting_value: root.update_o2_rest(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Rest Decrement"
                    setting_value: root.o2_rest_decrement
                    min_value: 5
                    max_value: 30
                    step_value: 5
                    accent_color: 0.25, 0.45, 0.85, 1
                    on_setting_value: root.update_o2_decrement(self.setting_value)

                Divider:

                RoundsStepper:
                    rounds_value: root.o2_rounds
                    accent_color: 0.25, 0.45, 0.85, 1
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

            # CO2 Section
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
                    setting_label: "Initial Hold"
                    setting_value: root.co2_initial_hold
                    min_value: 30
                    max_value: 180
                    step_value: 15
                    accent_color: 1.0, 0.7, 0.2, 1
                    on_setting_value: root.update_co2_hold(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Hold Increment"
                    setting_value: root.co2_hold_increment
                    min_value: 5
                    max_value: 30
                    step_value: 5
                    accent_color: 1.0, 0.7, 0.2, 1
                    on_setting_value: root.update_co2_increment(self.setting_value)

                Divider:

                SettingStepper:
                    setting_label: "Rest Time"
                    setting_value: root.co2_rest_time
                    min_value: 60
                    max_value: 300
                    step_value: 15
                    accent_color: 1.0, 0.7, 0.2, 1
                    on_setting_value: root.update_co2_rest(self.setting_value)

                Divider:

                RoundsStepper:
                    rounds_value: root.co2_rounds
                    accent_color: 1.0, 0.7, 0.2, 1
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
                    height: dp(48)

                    Label:
                        text: "Keep screen on"
                        font_size: sp(14)
                        color: 0.2, 0.2, 0.2, 1
                        text_size: self.size
                        halign: "left"
                        valign: "middle"

                    CheckBox:
                        active: root.keep_screen_on
                        on_active: root.keep_screen_on = self.active
                        size_hint_x: None
                        width: dp(48)
                        color: 0.15, 0.40, 0.65, 1

            # Reset Button
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
    o2_hold_time = NumericProperty(120)  # 2 minutes
    o2_initial_rest = NumericProperty(120)  # 2 minutes
    o2_rest_decrement = NumericProperty(15)  # 15 seconds
    o2_rounds = NumericProperty(8)

    # CO2 Table settings
    co2_initial_hold = NumericProperty(60)  # 1 minute
    co2_hold_increment = NumericProperty(15)  # 15 seconds
    co2_rest_time = NumericProperty(120)  # 2 minutes
    co2_rounds = NumericProperty(8)

    # General settings
    keep_screen_on = BooleanProperty(True)

    # Summaries
    o2_summary = StringProperty("")
    co2_summary = StringProperty("")

    # Setting keys for database persistence
    _setting_keys = {
        "o2_hold_time": float,
        "o2_initial_rest": float,
        "o2_rest_decrement": float,
        "o2_rounds": float,
        "co2_initial_hold": float,
        "co2_hold_increment": float,
        "co2_rest_time": float,
        "co2_rounds": float,
        "keep_screen_on": lambda v: v == "True",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._loading = True
        self._load_from_db()
        self._loading = False
        self._update_summaries()

    def on_keep_screen_on(self, instance, value):
        """Auto-save when keep_screen_on changes."""
        self._save_to_db()

    def _format_time(self, seconds):
        """Format seconds as M:SS."""
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}:{secs:02d}"

    def _update_summaries(self):
        """Update the training summary text."""
        # O2 summary: fixed hold, decreasing rest
        final_rest = max(
            15,
            self.o2_initial_rest - (self.o2_rounds - 1) * self.o2_rest_decrement,
        )
        self.o2_summary = (
            f"{int(self.o2_rounds)} rounds: "
            f"{self._format_time(self.o2_hold_time)} hold, "
            f"rest {self._format_time(self.o2_initial_rest)} → {self._format_time(final_rest)}"  # noqa E501
        )

        # CO2 summary: increasing hold, fixed rest
        final_hold = (
            self.co2_initial_hold + (self.co2_rounds - 1) * self.co2_hold_increment
        )
        self.co2_summary = (
            f"{int(self.co2_rounds)} rounds: hold {self._format_time(self.co2_initial_hold)} → "  # noqa E501
            f"{self._format_time(final_hold)}, {self._format_time(self.co2_rest_time)} rest"  # noqa E501
        )

    def update_o2_hold(self, value):
        self.o2_hold_time = value
        self._update_summaries()
        self._apply_settings()

    def update_o2_rest(self, value):
        self.o2_initial_rest = value
        self._update_summaries()
        self._apply_settings()

    def update_o2_decrement(self, value):
        self.o2_rest_decrement = value
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

    def update_co2_rest(self, value):
        self.co2_rest_time = value
        self._update_summaries()
        self._apply_settings()

    def update_co2_rounds(self, value):
        self.co2_rounds = value
        self._update_summaries()
        self._apply_settings()

    def reset_defaults(self):
        """Reset all settings to defaults."""
        self.o2_hold_time = 120
        self.o2_initial_rest = 120
        self.o2_rest_decrement = 15
        self.o2_rounds = 8
        self.co2_initial_hold = 60
        self.co2_hold_increment = 15
        self.co2_rest_time = 120
        self.co2_rounds = 8
        self.keep_screen_on = True
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
            o2_screen.initial_rest_time = int(self.o2_initial_rest)
            o2_screen.rest_decrement = int(self.o2_rest_decrement)
            o2_screen.total_rounds = int(self.o2_rounds)

            # Apply CO2 settings
            co2_screen = screen_manager.get_screen("co2_screen")
            co2_screen.initial_hold_time = int(self.co2_initial_hold)
            co2_screen.hold_increment = int(self.co2_hold_increment)
            co2_screen.rest_time = int(self.co2_rest_time)
            co2_screen.total_rounds = int(self.co2_rounds)
        except Exception:
            pass  # Settings will apply when screens are available
