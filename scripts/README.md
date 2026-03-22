# Scripts

## generate_screenshots.py

Generates store listing screenshots by rendering the actual Kivy app headlessly using Xvfb. The screenshots are pixel-perfect captures of the real app, not mockups.

### Prerequisites

**System packages** (Fedora/RHEL):

```bash
dnf install -y xorg-x11-server-Xvfb mesa-libGL mesa-libGL-devel mesa-libEGL \
    mesa-libEGL-devel mesa-dri-drivers SDL2 SDL2-devel SDL2_ttf SDL2_ttf-devel \
    SDL2_image SDL2_image-devel SDL2_mixer SDL2_mixer-devel gcc
```

On Debian/Ubuntu:

```bash
apt-get install -y xvfb libgl1-mesa-glx libgles2-mesa libsdl2-dev \
    libsdl2-ttf-dev libsdl2-image-dev libsdl2-mixer-dev
```

**Python 3.13 virtual environment** (Kivy 2.3.1 is not compatible with Python 3.14+):

```bash
uv venv --python 3.13 .venv-screenshots
uv pip install --python .venv-screenshots/bin/python "kivy[base]>=2.3.0"
```

### Usage

Generate all screenshots (phone + tablet):

```bash
xvfb-run -a -s "-screen 0 1920x2560x24" \
    .venv-screenshots/bin/python scripts/generate_screenshots.py
```

Generate for a specific device only:

```bash
# Phone (1080x1920, density=3)
xvfb-run -a -s "-screen 0 1080x1920x24" \
    .venv-screenshots/bin/python scripts/generate_screenshots.py --device phone

# Tablet (1920x2560, density=2)
xvfb-run -a -s "-screen 0 1920x2560x24" \
    .venv-screenshots/bin/python scripts/generate_screenshots.py --device tablet
```

### Output

Screenshots are saved to `screenshots/<device>/`:

```
screenshots/
  phone/
    home_1.png        # Home screen (empty heatmap)
    home_2.png        # Home screen (with practice data in heatmap)
    o2_1.png          # O2 Tables - ready state
    o2_2.png          # O2 Tables - mid-hold (round 3 of 8)
    co2_1.png         # CO2 Tables - ready state
    co2_2.png         # CO2 Tables - mid-hold (round 5 of 8)
    free_1.png        # Free Training - ready state
    free_2.png        # Free Training - active hold at 94s
    history_1.png     # Training History with session entries
  tablet/
    ...               # Same set at tablet resolution
```

Existing screenshots in the output directory are replaced on each run.

### How it works

1. Seeds the app database with sample training sessions (for history and heatmap screenshots).
2. Spawns a **subprocess per device** so Kivy initializes with the correct `KIVY_METRICS_DENSITY` and `KIVY_DPI` environment variables. This is required because Kivy reads density once at import time, and phone (3x) and tablet (2x) need different values for `dp()`/`sp()` to scale correctly.
3. Inside each subprocess: initializes the app, disables screen transition animations, navigates to each screen, optionally sets widget properties to simulate a mid-training state, then captures with `Window.screenshot()`.
