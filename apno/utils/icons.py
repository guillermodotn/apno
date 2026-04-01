"""Material Design Icons mapping for the app."""

# Icon codes from Material Design Icons
# Full list: https://pictogrammers.com/library/mdi/
ICONS = {
    # Navigation
    "menu": "\U000f035c",
    "home": "\U000f02dc",
    "cog": "\U000f0493",
    "information": "\U000f02fd",
    "close": "\U000f0156",
    "arrow-left": "\U000f004d",
    # Training
    "lungs": "\U000f1084",
    "weather-windy": "\U000f059d",
    "timer": "\U000f13ab",
    "timer-outline": "\U000f051b",
    "play": "\U000f040a",
    "pause": "\U000f03e4",
    "stop": "\U000f04db",
    # Actions
    "plus": "\U000f0415",
    "minus": "\U000f0374",
    "check": "\U000f012c",
    # Links
    "web": "\U000f059f",
    "github": "\U000f02a4",
    # Status
    "alert": "\U000f0026",
    "heart-pulse": "\U000f5f6c",
    # Settings
    "cellphone-screenshot": "\U000f0a35",
}


def icon(name: str) -> str:
    """Get the unicode character for an icon name."""
    return ICONS.get(name, "?")
