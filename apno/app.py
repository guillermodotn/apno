import os

import kivy
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.utils import platform

from apno.utils.audio import load_sounds

kivy.require("2.3.0")

# Set a reasonable default window size for desktop only
if platform not in ("android", "ios"):
    Window.size = (400, 700)

# Register Material Design Icons font
FONTS_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")
try:
    LabelBase.register(
        name="Icons",
        fn_regular=os.path.join(FONTS_DIR, "materialdesignicons-webfont.ttf"),
    )
except Exception as e:
    print(f"Warning: Could not register Icons font: {e}")


class Apno(App):
    def build(self):
        # Set window background color (cool white - Ocean Blue theme)
        Window.clearcolor = (0.97, 0.98, 1.0, 1)
        # Bind keyboard events for back button handling
        Window.bind(on_keyboard=self._on_keyboard)
        # Preload sound effects
        load_sounds()

    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        """Handle Android/iOS back button and ESC key.

        Returns True to consume the event (prevent app exit),
        False to allow the event to propagate (exit app).
        """
        # Key 27 is Android back button, 41 is ESC on desktop
        if key in (27, 41):
            return self._handle_back_button()
        return False

    def _handle_back_button(self):
        """Handle back button press - navigate back or exit."""
        if not self.root:
            return False

        # Check if navigation drawer is open and close it
        if hasattr(self.root.ids, "nav_drawer"):
            nav_drawer = self.root.ids.nav_drawer
            if hasattr(nav_drawer, "is_open") and nav_drawer.is_open:
                nav_drawer.close()
                return True

        # Get current screen
        screen_manager = self.root.ids.screen_manager
        current_screen = screen_manager.current

        # If not on home screen, go back to home
        if current_screen != "home":
            self.change_screen("home", "Apno")
            return True

        # On home screen - allow app to exit
        return False

    def change_screen(self, screen_name, title):
        """Navigate to a different screen."""
        # Update the app bar title
        self.root.ids.appbar.ids.title.text = title
        # Switch to the screen
        self.root.ids.screen_manager.current = screen_name
        # Close the navigation drawer if open
        if hasattr(self.root.ids, "nav_drawer"):
            self.root.ids.nav_drawer.close()


def main():
    """Entry point for the application."""
    Apno().run()
