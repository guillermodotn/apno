"""Session detail screen for viewing training session data."""

from datetime import datetime

from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from apno.utils.database import (
    get_contractions_for_session,
    get_session_by_id,
)
from apno.utils.icons import icon

Builder.load_string("""
#:import StyledCard apno.widgets.styled_card.StyledCard

<StatItem@BoxLayout>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(36)
    icon_text: ""
    icon_color: 0.4, 0.4, 0.4, 1
    stat_label: ""
    stat_value: ""

    Label:
        text: root.icon_text
        font_name: "Icons"
        font_size: sp(18)
        color: root.icon_color
        size_hint_x: None
        width: dp(32)

    Label:
        text: root.stat_label
        font_size: sp(14)
        color: 0.5, 0.5, 0.5, 1
        text_size: self.size
        halign: "left"
        valign: "middle"

    Label:
        text: root.stat_value
        font_size: sp(14)
        bold: True
        color: 0.2, 0.2, 0.2, 1
        text_size: self.size
        halign: "right"
        valign: "middle"
        size_hint_x: None
        width: dp(100)


<SectionLabel@Label>:
    size_hint_y: None
    height: dp(32)
    font_size: sp(13)
    bold: True
    color: 0.4, 0.4, 0.4, 1
    text_size: self.size
    halign: "left"
    valign: "middle"


<SessionDetailScreen>:
    ScrollView:
        do_scroll_x: False
        bar_width: dp(4)

        BoxLayout:
            id: content
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height
""")

TYPE_INFO = {
    "o2": {
        "name": "CO2 Table",
        "color": [1.0, 0.7, 0.2, 1],
    },
    "co2": {
        "name": "O2 Table",
        "color": [0.25, 0.45, 0.85, 1],
    },
    "free": {
        "name": "Free Training",
        "color": [0.4, 0.4, 0.8, 1],
    },
}


class ContractionTimeline(Widget):
    """Visual timeline showing contraction positions during a hold."""

    def __init__(self, hold_duration, contractions, accent_color, **kwargs):
        super().__init__(**kwargs)
        self.hold_duration = hold_duration
        self.contractions = contractions
        self.accent_color = accent_color
        self.size_hint_y = None
        self.height = dp(60)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *_args):
        self.canvas.clear()
        if self.hold_duration <= 0:
            return

        pad_x = dp(16)
        bar_y = self.y + self.height - dp(20)
        bar_w = self.width - pad_x * 2
        bar_h = dp(4)
        dot_r = dp(6)

        with self.canvas:
            # Track bar background
            Color(0.9, 0.9, 0.9, 1)
            RoundedRectangle(
                pos=(self.x + pad_x, bar_y - bar_h / 2),
                size=(bar_w, bar_h),
                radius=[dp(2)],
            )

            # Contraction dots
            Color(*self.accent_color)
            for c in self.contractions:
                t = c["seconds_into_hold"]
                x = self.x + pad_x + (t / self.hold_duration) * bar_w
                Ellipse(
                    pos=(x - dot_r, bar_y - dot_r),
                    size=(dot_r * 2, dot_r * 2),
                )

            # Start/end markers
            Color(0.6, 0.6, 0.6, 1)
            Line(
                points=[
                    self.x + pad_x,
                    bar_y - dp(8),
                    self.x + pad_x,
                    bar_y + dp(8),
                ],
                width=1,
            )
            Line(
                points=[
                    self.x + pad_x + bar_w,
                    bar_y - dp(8),
                    self.x + pad_x + bar_w,
                    bar_y + dp(8),
                ],
                width=1,
            )


class SessionDetailScreen(Screen):
    """Detail view for a single training session."""

    session_id = NumericProperty(0)

    def on_enter(self):
        """Load and display session data when screen is entered."""
        self._load_session()

    def _load_session(self):
        """Fetch session data and build the UI."""
        content = self.ids.content
        content.clear_widgets()

        session = get_session_by_id(self.session_id)
        if not session:
            content.add_widget(
                Label(
                    text="Session not found",
                    font_size=sp(16),
                    color=(0.5, 0.5, 0.5, 1),
                    size_hint_y=None,
                    height=dp(100),
                )
            )
            return

        training_type = session["training_type"]
        if training_type == "free":
            self._build_free_detail(content, session)
        elif training_type == "o2":
            self._build_o2_detail(content, session)
        elif training_type == "co2":
            self._build_co2_detail(content, session)

    def _format_duration(self, seconds):
        """Format seconds as M:SS."""
        if seconds is None:
            return "--:--"
        mins, secs = divmod(int(seconds), 60)
        return f"{mins}:{secs:02d}"

    def _format_datetime(self, dt_str):
        """Format a datetime string for display."""
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y at %I:%M %p")
        except (ValueError, TypeError):
            return dt_str or "Unknown"

    def _build_hero_card(self, content, value_text, label_text, color, is_best=False):
        """Build the large hero card with the main metric."""
        height = dp(190) if is_best else dp(160)
        card = Builder.load_string(f"""
StyledCard:
    orientation: "vertical"
    size_hint_y: None
    height: {height}
    padding: dp(16)
    spacing: dp(4)
""")

        # Value
        value_label = Label(
            text=value_text,
            font_size=sp(48),
            bold=True,
            color=color,
            size_hint_y=None,
            height=dp(60),
        )
        card.add_widget(value_label)

        # Label
        desc_label = Label(
            text=label_text,
            font_size=sp(14),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(24),
        )
        card.add_widget(desc_label)

        # Best badge
        if is_best:
            badge = BoxLayout(
                orientation="horizontal",
                size_hint=(None, None),
                size=(dp(140), dp(32)),
                pos_hint={"center_x": 0.5},
                spacing=dp(6),
            )

            trophy_icon = Label(
                text=icon("trophy"),
                font_name="Icons",
                font_size=sp(18),
                color=(0.85, 0.65, 0.13, 1),
                size_hint_x=None,
                width=dp(24),
            )
            badge.add_widget(trophy_icon)

            badge_label = Label(
                text="Personal Best",
                font_size=sp(14),
                bold=True,
                color=(0.85, 0.65, 0.13, 1),
            )
            badge.add_widget(badge_label)

            card.add_widget(badge)

        content.add_widget(card)

    def _build_info_card(self, content, items):
        """Build a card with stat rows.

        Args:
            content: Parent widget to add the card to.
            items: List of (icon_name, icon_color, label, value) tuples.
        """
        card = Builder.load_string("""
StyledCard:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(16), dp(8)
    spacing: 0
""")

        for i, (icon_name, icon_color, label, value) in enumerate(items):
            row = Builder.load_string(f"""
StatItem:
    icon_text: "{icon(icon_name)}"
    icon_color: {icon_color}
    stat_label: "{label}"
    stat_value: "{value}"
""")
            card.add_widget(row)

            # Add divider between rows (not after last)
            if i < len(items) - 1:
                divider = Widget(size_hint_y=None, height=dp(1))
                with divider.canvas:
                    Color(0.92, 0.92, 0.92, 1)
                    Rectangle(
                        pos=(divider.x + dp(32), divider.y),
                        size=(divider.width - dp(48), divider.height),
                    )
                divider.bind(
                    pos=lambda w, *a: w.canvas.ask_update(),
                    size=lambda w, *a: w.canvas.ask_update(),
                )
                card.add_widget(divider)

        content.add_widget(card)

    def _build_free_detail(self, content, session):
        """Build detail view for a free training session."""
        params = session.get("parameters", {}) or {}
        duration = session.get("duration_seconds", 0)
        completed = session.get("completed", 1)
        accent = TYPE_INFO["free"]["color"]

        # Check if this was a personal best
        is_best = params.get("is_alltime_best", False) or params.get(
            "is_session_best", False
        )

        # Hero card with hold time
        self._build_hero_card(
            content,
            self._format_duration(duration),
            "Hold Time",
            accent,
            is_best=is_best,
        )

        # Info card
        status_icon = "check-circle" if completed else "alert-circle"
        status_color = [0.2, 0.7, 0.4, 1] if completed else [0.8, 0.3, 0.3, 1]
        status_text = "Completed" if completed else "Incomplete"

        info_items = [
            (
                "calendar",
                [0.4, 0.4, 0.4, 1],
                "Date",
                self._format_datetime(session.get("completed_at")),
            ),
            (status_icon, status_color, "Status", status_text),
        ]
        self._build_info_card(content, info_items)

        # Contractions section
        contractions = get_contractions_for_session(session["id"])
        contraction_count = len(contractions)

        section_label = Label(
            text=f"Contractions ({contraction_count})",
            font_size=sp(13),
            bold=True,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(32),
            text_size=(None, None),
            halign="left",
        )
        section_label.bind(
            size=lambda w, s: setattr(w, "text_size", s),
        )
        content.add_widget(section_label)

        if contraction_count > 0 and duration and duration > 0:
            # Timeline card
            card = Builder.load_string("""
StyledCard:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(8), dp(8)
    spacing: dp(4)
""")

            # Timeline widget
            timeline = ContractionTimeline(
                hold_duration=duration,
                contractions=contractions,
                accent_color=accent,
            )
            card.add_widget(timeline)

            # Timeline labels (start and end)
            labels_row = BoxLayout(
                size_hint_y=None,
                height=dp(20),
                padding=(dp(16), 0),
            )
            labels_row.add_widget(
                Label(
                    text="0:00",
                    font_size=sp(11),
                    color=(0.6, 0.6, 0.6, 1),
                    halign="left",
                    text_size=(dp(40), None),
                )
            )
            labels_row.add_widget(Widget())  # spacer
            labels_row.add_widget(
                Label(
                    text=self._format_duration(duration),
                    font_size=sp(11),
                    color=(0.6, 0.6, 0.6, 1),
                    halign="right",
                    text_size=(dp(40), None),
                    size_hint_x=None,
                    width=dp(40),
                )
            )
            card.add_widget(labels_row)

            # Stats
            first_c = contractions[0]["seconds_into_hold"]
            if contraction_count > 1:
                last_c = contractions[-1]["seconds_into_hold"]
                avg_interval = (last_c - first_c) / (contraction_count - 1)
                stats_items = [
                    (
                        "chart-timeline",
                        accent,
                        "First contraction",
                        self._format_duration(first_c),
                    ),
                    ("timer-outline", accent, "Avg interval", f"{avg_interval:.0f}s"),
                ]
            else:
                stats_items = [
                    (
                        "chart-timeline",
                        accent,
                        "First contraction",
                        self._format_duration(first_c),
                    ),
                ]

            # Add stat rows inside the card
            for stat_icon, stat_color, stat_label, stat_value in stats_items:
                row = Builder.load_string(f"""
StatItem:
    icon_text: "{icon(stat_icon)}"
    icon_color: {stat_color}
    stat_label: "{stat_label}"
    stat_value: "{stat_value}"
""")
                card.add_widget(row)

            content.add_widget(card)
        else:
            # No contractions
            card = Builder.load_string("""
StyledCard:
    orientation: "vertical"
    size_hint_y: None
    height: dp(60)
    padding: dp(16)

    Label:
        text: "No contractions recorded"
        font_size: sp(13)
        color: 0.6, 0.6, 0.6, 1
""")
            content.add_widget(card)

    def _build_o2_detail(self, content, session):
        """Build detail view for an O2 table session."""
        params = session.get("parameters", {}) or {}
        duration = session.get("duration_seconds", 0)
        completed = session.get("completed", 1)
        rounds = session.get("rounds_completed", 0)
        accent = TYPE_INFO["o2"]["color"]

        # Hero card with session duration
        self._build_hero_card(
            content,
            self._format_duration(duration),
            "Session Duration",
            accent,
        )

        # Session info
        status_icon = "check-circle" if completed else "alert-circle"
        status_color = [0.2, 0.7, 0.4, 1] if completed else [0.8, 0.3, 0.3, 1]
        status_text = "Completed" if completed else "Incomplete"
        total_rounds = params.get("total_rounds", 8)

        info_items = [
            (
                "calendar",
                [0.4, 0.4, 0.4, 1],
                "Date",
                self._format_datetime(session.get("completed_at")),
            ),
            (status_icon, status_color, "Status", status_text),
            ("timer-outline", accent, "Rounds", f"{rounds}/{total_rounds}"),
        ]
        self._build_info_card(content, info_items)

        # Training parameters section
        hold_time = params.get("hold_time", 0)
        initial_breathe = params.get("initial_breathe_time", 120)
        breathe_decrement = params.get("breathe_decrement", 10)
        final_breathe = max(
            15, initial_breathe - (total_rounds - 1) * breathe_decrement
        )

        section_label = Label(
            text="Training Parameters",
            font_size=sp(13),
            bold=True,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(32),
            text_size=(None, None),
            halign="left",
        )
        section_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        content.add_widget(section_label)

        param_items = [
            ("timer", accent, "Hold Time", self._format_duration(hold_time)),
            (
                "lungs",
                [0.2, 0.7, 0.4, 1],
                "Breathe",
                f"{self._format_duration(initial_breathe)}"
                f" to {self._format_duration(final_breathe)}",
            ),
            (
                "minus",
                [0.4, 0.4, 0.4, 1],
                "Breathe Decrement",
                f"{int(breathe_decrement)}s/round",
            ),
        ]
        self._build_info_card(content, param_items)

    def _build_co2_detail(self, content, session):
        """Build detail view for a CO2 table session."""
        params = session.get("parameters", {}) or {}
        duration = session.get("duration_seconds", 0)
        completed = session.get("completed", 1)
        rounds = session.get("rounds_completed", 0)
        accent = TYPE_INFO["co2"]["color"]

        # Hero card with session duration
        self._build_hero_card(
            content,
            self._format_duration(duration),
            "Session Duration",
            accent,
        )

        # Session info
        status_icon = "check-circle" if completed else "alert-circle"
        status_color = [0.2, 0.7, 0.4, 1] if completed else [0.8, 0.3, 0.3, 1]
        status_text = "Completed" if completed else "Incomplete"
        total_rounds = params.get("total_rounds", 8)

        info_items = [
            (
                "calendar",
                [0.4, 0.4, 0.4, 1],
                "Date",
                self._format_datetime(session.get("completed_at")),
            ),
            (status_icon, status_color, "Status", status_text),
            ("timer-outline", accent, "Rounds", f"{rounds}/{total_rounds}"),
        ]
        self._build_info_card(content, info_items)

        # Training parameters section
        initial_hold = params.get("initial_hold_time", 30)
        hold_increment = params.get("hold_increment", 10)
        breathe_time = params.get("breathe_time", 120)
        final_hold = initial_hold + (total_rounds - 1) * hold_increment

        section_label = Label(
            text="Training Parameters",
            font_size=sp(13),
            bold=True,
            color=(0.4, 0.4, 0.4, 1),
            size_hint_y=None,
            height=dp(32),
            text_size=(None, None),
            halign="left",
        )
        section_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        content.add_widget(section_label)

        param_items = [
            (
                "timer",
                accent,
                "Hold",
                f"{self._format_duration(initial_hold)}"
                f" to {self._format_duration(final_hold)}",
            ),
            (
                "plus",
                [0.4, 0.4, 0.4, 1],
                "Hold Increment",
                f"{int(hold_increment)}s/round",
            ),
            (
                "lungs",
                [0.2, 0.7, 0.4, 1],
                "Breathe Time",
                self._format_duration(breathe_time),
            ),
        ]
        self._build_info_card(content, param_items)
