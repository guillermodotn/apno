"""History screen showing all training sessions."""

from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from apno.utils.database import (
    get_contraction_count_for_session,
    get_practice_sessions,
)
from apno.utils.icons import icon

Builder.load_string("""
#:import ClickableCard apno.widgets.styled_card.ClickableCard

<HistoryEntry@ClickableCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(80)
    spacing: dp(12)
    session_id: 0
    training_type: ""
    completed_at: ""
    duration_text: ""
    rounds_text: ""
    icon_color: 0.5, 0.5, 0.5, 1
    icon_name: ""

    Label:
        text: root.icon_name
        font_name: "Icons"
        font_size: sp(32)
        color: root.icon_color
        size_hint: None, None
        size: dp(48), dp(48)
        pos_hint: {"center_y": 0.5}

    BoxLayout:
        orientation: "vertical"
        spacing: dp(4)

        Label:
            text: root.training_type
            font_size: sp(16)
            bold: True
            color: 0.1, 0.1, 0.1, 1
            text_size: self.size
            halign: "left"
            valign: "bottom"
            size_hint_y: 0.5

        Label:
            text: root.completed_at
            font_size: sp(13)
            color: 0.5, 0.5, 0.5, 1
            text_size: self.size
            halign: "left"
            valign: "top"
            size_hint_y: 0.5

    BoxLayout:
        orientation: "vertical"
        size_hint_x: None
        width: dp(100)
        spacing: dp(2)

        Label:
            text: root.duration_text
            font_size: sp(14)
            bold: True
            color: 0.3, 0.3, 0.3, 1
            text_size: self.size
            halign: "right"
            valign: "bottom"
            size_hint_y: 0.5

        Label:
            text: root.rounds_text
            font_size: sp(12)
            color: 0.5, 0.5, 0.5, 1
            text_size: self.size
            halign: "right"
            valign: "top"
            size_hint_y: 0.5


<HistoryScreen>:
    ScrollView:
        do_scroll_x: False
        bar_width: dp(4)
        bar_color: 0.5, 0.5, 0.5, 0.5
        bar_inactive_color: 0.5, 0.5, 0.5, 0.2

        BoxLayout:
            id: history_container
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height
""")


class HistoryScreen(Screen):
    """Screen showing all training history."""

    def on_enter(self):
        """Refresh the history list when entering the screen."""
        self._load_history()

    def _on_entry_tap(self, entry):
        """Navigate to the session detail screen."""
        app = App.get_running_app()
        detail = app.root.ids.screen_manager.get_screen("session_detail")
        detail.session_id = entry.session_id
        app.change_screen("session_detail", "Session Details")

    def _load_history(self):
        """Load and display all training sessions."""
        container = self.ids.history_container
        sessions = get_practice_sessions(limit=100)

        # Clear all entries
        container.clear_widgets()

        if not sessions:
            container.add_widget(
                Label(
                    text="No training sessions yet.\nStart your first training!",
                    font_size=sp(16),
                    color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None,
                    height=dp(100),
                    halign="center",
                    text_size=(None, None),
                )
            )
            return

        # Training type display names and colors
        type_info = {
            "o2": {
                "name": "O2 Tables",
                "color": [0.25, 0.45, 0.85, 1],
                "icon": "lungs",
            },
            "co2": {
                "name": "CO2 Tables",
                "color": [1.0, 0.7, 0.2, 1],
                "icon": "weather-windy",
            },
            "free": {
                "name": "Free Training",
                "color": [0.4, 0.4, 0.8, 1],
                "icon": "timer-outline",
            },
        }

        for session in sessions:
            training_type = session.get("training_type", "")
            info = type_info.get(
                training_type,
                {
                    "name": training_type.title(),
                    "color": [0.5, 0.5, 0.5, 1],
                    "icon": "dumbbell",
                },
            )

            # Format date
            completed_at = session.get("completed_at", "")
            if completed_at:
                try:
                    dt = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %d, %Y at %I:%M %p")
                except ValueError:
                    date_str = str(completed_at)
            else:
                date_str = "Unknown date"

            # Format duration
            duration = session.get("duration_seconds")
            if duration:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                duration_str = f"{minutes}m {seconds}s"
            else:
                duration_str = ""

            # Format rounds
            rounds = session.get("rounds_completed")
            rounds_str = f"{rounds} rounds" if rounds else ""

            # Get contraction count
            session_id = session.get("id")
            contraction_count = (
                get_contraction_count_for_session(session_id) if session_id else 0
            )
            contractions_str = (
                f"{contraction_count} contractions" if contraction_count > 0 else ""
            )

            # Combine rounds and contractions for display
            details_str = rounds_str
            if contractions_str:
                details_str = (
                    f"{rounds_str} | {contractions_str}"
                    if rounds_str
                    else contractions_str
                )

            # Dim incomplete sessions
            completed = session.get("completed", 1)
            if not completed:
                date_str += " (incomplete)"
                info["color"] = [c * 0.5 for c in info["color"][:3]] + [0.5]

            entry = Builder.load_string(f"""
HistoryEntry:
    session_id: {session["id"]}
    training_type: "{info["name"]}"
    completed_at: "{date_str}"
    duration_text: "{duration_str}"
    rounds_text: "{details_str}"
    icon_color: {info["color"]}
    icon_name: "{icon(info["icon"])}"
""")
            entry.bind(on_release=self._on_entry_tap)
            container.add_widget(entry)
