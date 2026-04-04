import webbrowser

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from apno import __version__
from apno.utils.icons import icon

WEBSITE_URL = "https://guillermodotn.github.io/apno/"
GITHUB_URL = "https://github.com/guillermodotn/apno"

Builder.load_string("""
#:import ClickableCard apno.widgets.styled_card.ClickableCard

<AboutScreen>:
    ScrollView:
        BoxLayout:
            orientation: "vertical"
            padding: dp(24)
            spacing: dp(16)
            size_hint_y: None
            height: self.minimum_height

            Image:
                source: "apno/assets/images/logo.png"
                size_hint_y: None
                height: dp(120)

            Label:
                text: "Apno"
                font_size: sp(28)
                bold: True
                color: 0.2, 0.5, 0.9, 1
                size_hint_y: None
                height: dp(40)

            Label:
                text: root.version_text
                font_size: sp(14)
                color: 0.5, 0.5, 0.5, 1
                size_hint_y: None
                height: dp(20)

            Label:
                text: root.description_text
                font_size: sp(14)
                color: 0.4, 0.4, 0.4, 1
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: "center"

            Widget:
                size_hint_y: None
                height: dp(1)
                canvas:
                    Color:
                        rgba: 0.9, 0.9, 0.9, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

            ClickableCard:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(72)
                spacing: dp(12)
                on_release: root.open_website()

                Label:
                    text: root.icon_web
                    font_name: "Icons"
                    font_size: sp(28)
                    color: 0.15, 0.4, 0.65, 1
                    size_hint_x: None
                    width: dp(32)

                BoxLayout:
                    orientation: "vertical"
                    spacing: dp(2)

                    Label:
                        text: "Website"
                        font_size: sp(16)
                        bold: True
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: sp(22)
                        text_size: self.size
                        halign: "left"
                        valign: "bottom"

                    Label:
                        text: "guillermodotn.github.io/apno"
                        font_size: sp(12)
                        color: 0.5, 0.5, 0.5, 1
                        size_hint_y: None
                        height: sp(18)
                        text_size: self.size
                        halign: "left"
                        valign: "top"

            ClickableCard:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(72)
                spacing: dp(12)
                on_release: root.open_github()

                Label:
                    text: root.icon_github
                    font_name: "Icons"
                    font_size: sp(28)
                    color: 0.2, 0.2, 0.2, 1
                    size_hint_x: None
                    width: dp(32)

                BoxLayout:
                    orientation: "vertical"
                    spacing: dp(2)

                    Label:
                        text: "Source Code"
                        font_size: sp(16)
                        bold: True
                        color: 0.2, 0.2, 0.2, 1
                        size_hint_y: None
                        height: sp(22)
                        text_size: self.size
                        halign: "left"
                        valign: "bottom"

                    Label:
                        text: "guillermodotn/apno"
                        font_size: sp(12)
                        color: 0.5, 0.5, 0.5, 1
                        size_hint_y: None
                        height: sp(18)
                        text_size: self.size
                        halign: "left"
                        valign: "top"

            Widget:
                size_hint_y: None
                height: dp(1)
                canvas:
                    Color:
                        rgba: 0.9, 0.9, 0.9, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

            BoxLayout:
                size_hint_y: None
                height: dp(32)
                spacing: dp(8)

                Label:
                    text: root.icon_alert
                    font_name: "Icons"
                    font_size: sp(24)
                    color: 0.9, 0.3, 0.3, 1
                    size_hint_x: None
                    width: dp(32)

                Label:
                    text: "Safety Guidelines"
                    font_size: sp(18)
                    bold: True
                    color: 0.9, 0.3, 0.3, 1
                    text_size: self.size
                    halign: "left"
                    valign: "middle"

            Label:
                text: root.safety_text
                font_size: sp(14)
                color: 0.4, 0.4, 0.4, 1
                size_hint_y: None
                height: dp(140)
                text_size: self.width, None
                halign: "left"

            Widget:
                size_hint_y: None
                height: dp(24)
""")


class AboutScreen(Screen):
    version_text = StringProperty(f"Version {__version__}")
    description_text = StringProperty(
        "Open-source apnea training for freedivers,"
        " spearfishers, and anyone looking to improve"
        " their breath-hold capacity."
    )
    icon_web = StringProperty(icon("web"))
    icon_github = StringProperty(icon("github"))
    icon_alert = StringProperty(icon("alert"))
    safety_text = StringProperty(
        "- Never practice in water alone\n"
        "- Train in a safe environment\n"
        "- Stop if dizzy or unwell\n"
        "- Consult doctor if needed\n"
        "- Never hyperventilate\n"
        "- Progress gradually"
    )

    def open_website(self):
        webbrowser.open(WEBSITE_URL)

    def open_github(self):
        webbrowser.open(GITHUB_URL)
