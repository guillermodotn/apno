"""Monthly practice heatmap widget."""

from calendar import monthrange
from datetime import datetime, timedelta

from kivy.app import App
from kivy.graphics import Color, Mesh, RoundedRectangle
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from apno.utils.database import get_training_types_by_date

Builder.load_string("""
<DaySquare>:
    size_hint: 1, None
    height: self.width if self.width > 0 else dp(20)

<MonthGrid>:
    orientation: "vertical"
    spacing: dp(2)
    size_hint_y: None
    height: self.minimum_height

    Label:
        text: root.month_title
        font_size: sp(13)
        bold: True
        color: 0.3, 0.3, 0.3, 1
        size_hint_y: None
        height: dp(20)
        halign: "center"
        text_size: self.size
        valign: "middle"

    GridLayout:
        id: weekday_headers
        cols: 7
        size_hint_y: None
        height: dp(14)
        spacing: dp(2)

    GridLayout:
        id: days_grid
        cols: 7
        spacing: dp(2)
        size_hint_y: None
        height: self.minimum_height

<MonthlyHeatmap>:
    orientation: "vertical"
    size_hint_y: None
    height: self.minimum_height
    padding: dp(12)
    spacing: dp(8)

    BoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(24)

        Label:
            text: "Practice Activity"
            font_size: sp(15)
            bold: True
            color: 0.2, 0.2, 0.2, 1
            halign: "left"
            text_size: self.size
            valign: "middle"

        Label:
            text: root.streak_text
            font_size: sp(13)
            color: 0.4, 0.4, 0.4, 1
            halign: "right"
            text_size: self.size
            valign: "middle"

    BoxLayout:
        id: months_container
        orientation: "horizontal"
        spacing: dp(16)
        size_hint_y: None
        height: max(prev_month_grid.height, curr_month_grid.height) if prev_month_grid.height > 0 else dp(150)

        MonthGrid:
            id: prev_month_grid
            size_hint_x: 0.5

        MonthGrid:
            id: curr_month_grid
            size_hint_x: 0.5
""")  # noqa


class DaySquare(Widget):
    """A single day square in the heatmap."""

    bg_color = ListProperty([0.9, 0.9, 0.9, 1])
    bg_color2 = ListProperty([0.9, 0.9, 0.9, 1])
    is_split = NumericProperty(0)  # 0 = single color, 1 = diagonal split
    day_num = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(bg_color=self._update_canvas, bg_color2=self._update_canvas)
        self.bind(is_split=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            if self.is_split:
                # Draw diagonal split: bottom-left triangle (CO2 - orange)
                Color(*self.bg_color)
                Mesh(
                    vertices=[
                        self.x,
                        self.y,
                        0,
                        0,  # bottom-left
                        self.x + self.width,
                        self.y,
                        0,
                        0,  # bottom-right
                        self.x,
                        self.y + self.height,
                        0,
                        0,  # top-left
                    ],
                    indices=[0, 1, 2],
                    mode="triangles",
                )
                # Draw diagonal split: top-right triangle (O2 - blue)
                Color(*self.bg_color2)
                Mesh(
                    vertices=[
                        self.x + self.width,
                        self.y,
                        0,
                        0,  # bottom-right
                        self.x + self.width,
                        self.y + self.height,
                        0,
                        0,  # top-right
                        self.x,
                        self.y + self.height,
                        0,
                        0,  # top-left
                    ],
                    indices=[0, 1, 2],
                    mode="triangles",
                )
            else:
                # Single color
                Color(*self.bg_color)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[3])


class MonthGrid(BoxLayout):
    """A single month grid with title and days."""

    month_title = StringProperty("")

    def on_kv_post(self, base_widget):
        """Called after kv rules are applied."""
        self._build_weekday_headers()

    def _build_weekday_headers(self):
        """Build the weekday header row."""
        weekdays = ["M", "T", "W", "T", "F", "S", "S"]
        grid = self.ids.weekday_headers
        grid.clear_widgets()
        for day in weekdays:
            lbl = Label(
                text=day,
                font_size="10sp",
                color=[0.5, 0.5, 0.5, 1],
                size_hint=(1, 1),
                halign="center",
                valign="middle",
            )
            lbl.bind(size=lbl.setter("text_size"))
            grid.add_widget(lbl)

    # Training type colors (Amber & Deep Blue - Fire & Water theme)
    CO2_COLOR = [1.0, 0.7, 0.2, 1]  # Amber
    O2_COLOR = [0.25, 0.45, 0.85, 1]  # Deep Blue
    EMPTY_COLOR = [0.92, 0.92, 0.92, 1]
    FUTURE_COLOR = [0.96, 0.96, 0.96, 1]

    def build_month(
        self,
        year: int,
        month: int,
        practice_data: dict,
        today_year: int,
        today_month: int,
        today_day: int,
    ):
        """Build the calendar grid for a specific month.

        Args:
            practice_data: Dictionary mapping date strings to sets of training types
        """
        # Set month title
        month_date = datetime(year, month, 1)
        self.month_title = month_date.strftime("%b %Y")

        grid = self.ids.days_grid
        grid.clear_widgets()

        # Get first day of month (0=Monday, 6=Sunday)
        first_weekday, num_days = monthrange(year, month)

        # Add empty squares for days before the 1st
        for _ in range(first_weekday):
            square = DaySquare(bg_color=[0, 0, 0, 0])
            grid.add_widget(square)

        # Add squares for each day
        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            training_types = practice_data.get(date_str, set())

            is_future = (
                year > today_year
                or (year == today_year and month > today_month)
                or (year == today_year and month == today_month and day > today_day)
            )

            if is_future:
                square = DaySquare(bg_color=self.FUTURE_COLOR, day_num=day)
            elif "co2" in training_types and "o2" in training_types:
                # Both trainings - diagonal split
                square = DaySquare(
                    bg_color=self.O2_COLOR,
                    bg_color2=self.CO2_COLOR,
                    is_split=1,
                    day_num=day,
                )
            elif "co2" in training_types:
                # O2 Table (internal co2) - blue
                square = DaySquare(bg_color=self.O2_COLOR, day_num=day)
            elif "o2" in training_types:
                # CO2 Table (internal o2) - amber
                square = DaySquare(bg_color=self.CO2_COLOR, day_num=day)
            else:
                # No practice
                square = DaySquare(bg_color=self.EMPTY_COLOR, day_num=day)

            grid.add_widget(square)

        # Fill remaining squares
        remaining = (7 - ((first_weekday + num_days) % 7)) % 7
        for _ in range(remaining):
            square = DaySquare(bg_color=[0, 0, 0, 0])
            grid.add_widget(square)


class MonthlyHeatmap(ButtonBehavior, BoxLayout):
    """A GitHub-style monthly heatmap showing practice days for two months."""

    streak_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._update_bg, size=self._update_bg)
        self._update_bg()

    def on_press(self):
        """Visual feedback when pressed."""
        self._original_bg = [1, 1, 1, 1]
        self._update_bg_pressed()

    def on_release(self):
        """Restore original appearance and navigate to history."""
        self._update_bg()
        # Navigate to history screen
        if hasattr(self, "app") and self.app:
            self.app.change_screen("history_screen", "Training History")
        else:
            # Try to get app from parent

            app = App.get_running_app()
            if app:
                app.change_screen("history_screen", "Training History")

    def _update_bg_pressed(self, *args):
        """Update background when pressed."""
        self.canvas.before.clear()
        with self.canvas.before:
            # Shadow (slight offset)
            Color(0, 0, 0, 0.08)
            RoundedRectangle(pos=(self.x + 2, self.y - 2), size=self.size, radius=[12])
            # Background (slightly darker)
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

    def _update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.08)
            RoundedRectangle(pos=(self.x + 2, self.y - 2), size=self.size, radius=[12])
            # Background
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

    def on_kv_post(self, base_widget):
        """Called after kv rules are applied."""
        self.refresh()

    def refresh(self):
        """Refresh the heatmap with current data."""
        now = datetime.now()
        curr_year = now.year
        curr_month = now.month
        today_day = now.day

        # Calculate previous month
        if curr_month == 1:
            prev_year = curr_year - 1
            prev_month = 12
        else:
            prev_year = curr_year
            prev_month = curr_month - 1

        # Get practice data for both months (62 days covers both)
        practice_data = get_training_types_by_date(days=62)

        # Calculate current streak (consecutive days with any practice)
        streak = self._calculate_streak(practice_data)
        self.streak_text = (
            f"{streak} day streak" if streak == 1 else f"{streak} day streak"
        )

        # Build both month grids
        self.ids.prev_month_grid.build_month(
            prev_year, prev_month, practice_data, curr_year, curr_month, today_day
        )
        self.ids.curr_month_grid.build_month(
            curr_year, curr_month, practice_data, curr_year, curr_month, today_day
        )

    def _calculate_streak(self, practice_data: dict) -> int:
        """Calculate the current streak of consecutive practice days.

        Counts backwards from today, counting consecutive days with any practice.
        The streak includes today if practiced, otherwise starts from last practice day.

        Args:
            practice_data: Dictionary mapping date strings to sets of training types

        Returns:
            Number of consecutive days with practice
        """
        today = datetime.now().date()
        streak = 0
        check_date = today

        while True:
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in practice_data and practice_data[date_str]:
                streak += 1
                check_date = check_date - timedelta(days=1)
            else:
                break

        return streak
