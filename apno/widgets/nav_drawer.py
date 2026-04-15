from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from apno.utils.icons import icon

DRAWER_WIDTH = 280  # in dp units

Builder.load_string("""
<NavDrawerItem>:
    size_hint_y: None
    height: dp(48)
    padding: dp(16), 0
    spacing: dp(16)

    Label:
        text: root.icon_char
        font_name: "Icons"
        font_size: sp(24)
        size_hint_x: None
        width: dp(32)
        color: root.text_color

    Label:
        text: root.text
        font_size: sp(16)
        color: root.text_color
        text_size: self.size
        halign: "left"
        valign: "center"


<NavDrawer>:
    orientation: "vertical"
    size_hint: None, 1
    width: dp(280)
    padding: 0, dp(16)
    spacing: dp(4)

    Label:
        text: "Apno"
        font_size: sp(24)
        bold: True
        color: 0.15, 0.40, 0.65, 1
        size_hint_y: None
        height: dp(56)
        text_size: self.width - dp(32), None
        halign: "left"
        padding: dp(16), 0

    Widget:
        size_hint_y: None
        height: dp(1)
        canvas:
            Color:
                rgba: 0.82, 0.88, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size

    NavDrawerItem:
        icon_name: "home"
        text: "Home"
        on_release: root.nav_to("home", "Apno")

    NavDrawerItem:
        icon_name: "weather-windy"
        text: "CO2 Table"
        on_release: root.nav_to("o2_screen", "CO2 Table")

    NavDrawerItem:
        icon_name: "lungs"
        text: "O2 Table"
        on_release: root.nav_to("co2_screen", "O2 Table")

    NavDrawerItem:
        icon_name: "timer-outline"
        text: "Free Training"
        on_release: root.nav_to("free_screen", "Free Training")

    NavDrawerItem:
        icon_name: "history"
        text: "History"
        on_release: root.nav_to("history_screen", "History")

    Widget:
        size_hint_y: None
        height: dp(1)
        canvas:
            Color:
                rgba: 0.82, 0.88, 0.95, 1
            Rectangle:
                pos: self.pos
                size: self.size

    NavDrawerItem:
        icon_name: "cog"
        text: "Settings"
        on_release: root.nav_to("settings_screen", "Settings")

    NavDrawerItem:
        icon_name: "information"
        text: "About"
        on_release: root.nav_to("about_screen", "About")

    Widget:
        # Spacer
""")


class NavDrawerItem(ButtonBehavior, BoxLayout):
    """A navigation drawer menu item."""

    icon_name = StringProperty("")
    icon_char = StringProperty("")
    text = StringProperty("")
    text_color = ColorProperty([0.12, 0.18, 0.28, 1])  # Dark Navy

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(icon_name=self._update_icon)
        # Defer icon update to after init
        from kivy.clock import Clock

        Clock.schedule_once(lambda dt: self._update_icon(), 0)

    def _update_icon(self, *args):
        self.icon_char = icon(self.icon_name) if self.icon_name else ""

    def on_press(self):
        self._update_bg(0.92)

    def on_release(self):
        self._update_bg(1)

    def _update_bg(self, value):
        self.canvas.before.clear()
        if value < 1:
            with self.canvas.before:
                Color(value, value, value, 1)
                RoundedRectangle(pos=self.pos, size=self.size, radius=[8])


class NavDrawer(BoxLayout):
    """Navigation drawer content."""

    def nav_to(self, screen_name, title):
        """Navigate to a screen and close the drawer."""
        from kivy.app import App

        app = App.get_running_app()
        app.change_screen(screen_name, title)


class NavDrawerContainer(Widget):
    """Container that handles the drawer sliding and overlay."""

    is_open = BooleanProperty(False)
    drawer_x = NumericProperty(0)
    overlay_opacity = NumericProperty(0)
    bg_color = ColorProperty([0.92, 0.96, 1.0, 1])  # Light Sky Blue

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drawer = NavDrawer()
        self.add_widget(self.drawer)
        self.bind(pos=self._update_layout, size=self._update_layout)
        self.bind(drawer_x=self._update_layout)
        self.bind(overlay_opacity=self._update_layout)
        # Start closed
        self.drawer_x = -dp(DRAWER_WIDTH)
        self._update_layout()

    def _update_layout(self, *args):
        # Update drawer position
        self.drawer.pos = (self.drawer_x, self.y)
        self.drawer.height = self.height

        # Draw overlay and drawer background
        self.canvas.before.clear()
        with self.canvas.before:
            # Overlay
            if self.overlay_opacity > 0:
                Color(0, 0, 0, self.overlay_opacity * 0.5)
                Rectangle(pos=self.pos, size=self.size)
            # Drawer background
            Color(*self.bg_color)
            Rectangle(
                pos=(self.drawer_x, self.y),
                size=(self.drawer.width, self.height),
            )

    def toggle(self):
        if self.is_open:
            self.close()
        else:
            self.open()

    def open(self):
        self.is_open = True
        anim = Animation(drawer_x=0, overlay_opacity=1, duration=0.25, t="out_cubic")
        anim.start(self)

    def close(self):
        self.is_open = False
        anim = Animation(
            drawer_x=-dp(DRAWER_WIDTH),
            overlay_opacity=0,
            duration=0.2,
            t="out_cubic",
        )
        anim.start(self)

    def on_touch_down(self, touch):
        if self.is_open:
            # Check if touch is outside drawer
            if touch.x > self.drawer.width:
                self.close()
                return True
        return super().on_touch_down(touch)
