from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from apno.utils.icons import icon

Builder.load_string("""
#:import ClickableCard apno.widgets.styled_card.ClickableCard
#:import MonthlyHeatmap apno.widgets.monthly_heatmap.MonthlyHeatmap

<TrainingCard@ClickableCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: dp(100)
    spacing: dp(16)
    training_title: ""
    training_desc: ""
    training_icon: ""
    training_color: 0.2, 0.6, 0.9, 1

    Label:
        text: root.training_icon
        font_name: "Icons"
        font_size: sp(40)
        size_hint: None, None
        size: dp(56), dp(56)
        pos_hint: {"center_y": 0.5}
        color: root.training_color

    BoxLayout:
        orientation: "vertical"
        spacing: dp(4)

        Label:
            text: root.training_title
            font_size: sp(18)
            bold: True
            color: 0.1, 0.1, 0.1, 1
            text_size: self.size
            halign: "left"
            valign: "bottom"
            size_hint_y: 0.4

        Label:
            text: root.training_desc
            font_size: sp(14)
            color: 0.5, 0.5, 0.5, 1
            text_size: self.size
            halign: "left"
            valign: "top"
            size_hint_y: 0.6


<HomeScreen>:
    ScrollView:
        do_scroll_x: False
        bar_width: dp(4)
        bar_color: 0.5, 0.5, 0.5, 0.5
        bar_inactive_color: 0.5, 0.5, 0.5, 0.2

        BoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height

            MonthlyHeatmap:
                id: heatmap

            Label:
                text: "Choose Your Training"
                font_size: sp(16)
                bold: True
                color: 0.1, 0.1, 0.1, 1
                size_hint_y: None
                height: dp(28)

            TrainingCard:
                training_title: "CO2 Table"
                training_desc: "Fixed hold, decreasing breathe. Builds CO2 tolerance."
                training_icon: root.icon_wind
                training_color: 1.0, 0.7, 0.2, 1
                on_release: app.change_screen("o2_screen", "CO2 Table")

            TrainingCard:
                training_title: "O2 Table"
                training_desc: "Increasing hold, fixed breathe. Trains O2 deprivation."
                training_icon: root.icon_lungs
                training_color: 0.25, 0.45, 0.85, 1
                on_release: app.change_screen("co2_screen", "O2 Table")

            TrainingCard:
                training_title: "Free Training"
                training_desc: "Practice breath holds at your own pace."
                training_icon: root.icon_timer
                training_color: 0.4, 0.4, 0.8, 1
                on_release: app.change_screen("free_screen", "Free Training")

            Label:
                text: "Tip: Start with CO2 tables, then progress to O2 tables."
                font_size: sp(13)
                color: 0.5, 0.5, 0.5, 1
                size_hint_y: None
                height: dp(32)
                text_size: self.width, None
                halign: "center"
                valign: "middle"
""")


class HomeScreen(Screen):
    # Icon properties for use in kv
    icon_lungs = StringProperty(icon("lungs"))
    icon_wind = StringProperty(icon("weather-windy"))
    icon_timer = StringProperty(icon("timer-outline"))

    def on_enter(self):
        """Refresh heatmap when entering the screen."""
        if hasattr(self, "ids") and "heatmap" in self.ids:
            self.ids.heatmap.refresh()
