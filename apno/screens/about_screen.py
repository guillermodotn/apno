from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from apno import __version__
from apno.utils.icons import icon

Builder.load_string("""
#:import StyledCard apno.widgets.styled_card.StyledCard

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

            Widget:
                size_hint_y: None
                height: dp(1)
                canvas:
                    Color:
                        rgba: 0.9, 0.9, 0.9, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size

            Label:
                text: "About Apnea Training"
                font_size: sp(18)
                bold: True
                color: 0.2, 0.2, 0.2, 1
                size_hint_y: None
                height: dp(32)
                text_size: self.size
                halign: "left"
                valign: "middle"

            Label:
                text: "Apnea training improves breath-holding through practice."
                font_size: sp(14)
                color: 0.4, 0.4, 0.4, 1
                size_hint_y: None
                height: dp(48)
                text_size: self.width, None
                halign: "left"

            StyledCard:
                orientation: "vertical"
                size_hint_y: None
                height: dp(100)
                spacing: dp(4)

                Label:
                    text: "O2 Tables"
                    font_size: sp(16)
                    bold: True
                    color: 0.2, 0.7, 0.4, 1
                    size_hint_y: None
                    height: dp(24)
                    text_size: self.size
                    halign: "left"
                    valign: "middle"

                Label:
                    text: "Fixed hold with decreasing rest. Improves O2 efficiency."
                    font_size: sp(14)
                    color: 0.4, 0.4, 0.4, 1
                    text_size: self.width - dp(32), None
                    halign: "left"

            StyledCard:
                orientation: "vertical"
                size_hint_y: None
                height: dp(100)
                spacing: dp(4)

                Label:
                    text: "CO2 Tables"
                    font_size: sp(16)
                    bold: True
                    color: 0.9, 0.5, 0.2, 1
                    size_hint_y: None
                    height: dp(24)
                    text_size: self.size
                    halign: "left"
                    valign: "middle"

                Label:
                    text: "Increasing hold with fixed rest. Builds CO2 tolerance."
                    font_size: sp(14)
                    color: 0.4, 0.4, 0.4, 1
                    text_size: self.width - dp(32), None
                    halign: "left"

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
    icon_alert = StringProperty(icon("alert"))
    safety_text = StringProperty(
        "• Never practice in water alone\n"
        "• Train in a safe environment\n"
        "• Stop if dizzy or unwell\n"
        "• Consult doctor if needed\n"
        "• Never hyperventilate\n"
        "• Progress gradually"
    )
