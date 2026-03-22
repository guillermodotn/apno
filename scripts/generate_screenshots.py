#!/usr/bin/env python3
"""
Generate store listing screenshots by rendering the actual Kivy app.

Requires Xvfb for headless rendering. Run via:

    xvfb-run -a -s "-screen 0 1920x2560x24" \\
        .venv-screenshots/bin/python scripts/generate_screenshots.py

    # Phone only:
    xvfb-run -a -s "-screen 0 1080x1920x24" \\
        .venv-screenshots/bin/python scripts/generate_screenshots.py --device phone
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Must be set before any Kivy import (including transitive ones)
os.environ.setdefault("KIVY_LOG_MODE", "PYTHON")
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_LOG_LEVEL", "warning")

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def _seed_database():
    """Insert sample training sessions spread across the past month.

    Creates a realistic training history with sessions on ~20 of the last
    30 days so the heatmap looks populated. Durations are kept realistic
    (hold times between 60-120s, session totals between 8-16 minutes).
    """
    import json
    import random
    from datetime import datetime, timedelta

    sys.path.insert(0, str(PROJECT_ROOT))
    from apno.utils.database import get_connection, init_db

    init_db()
    conn = get_connection()

    random.seed(42)  # deterministic so screenshots are reproducible
    today = datetime.now()

    # Pick ~20 days out of the last 30 to have sessions on
    training_days = sorted(random.sample(range(1, 31), 20), reverse=True)

    sessions = []
    for days_ago in training_days:
        day = today - timedelta(days=days_ago)

        # Each day: 1-3 sessions mixing o2, co2, and occasionally free
        day_types = random.choice(
            [
                ["o2"],
                ["co2"],
                ["o2", "co2"],
                ["co2", "o2"],
                ["o2", "free"],
                ["co2", "free"],
                ["o2", "co2", "free"],
            ]
        )

        for i, training_type in enumerate(day_types):
            # Stagger times throughout the day (morning/evening)
            hour = random.choice([7, 8, 9, 18, 19, 20])
            minute = random.randint(0, 45)
            ts = day.replace(hour=hour + i, minute=minute, second=0)
            completed_at = ts.strftime("%Y-%m-%d %H:%M:%S")

            if training_type == "free":
                # Free hold: 60-115 seconds
                hold_time = random.randint(60, 115)
                contractions = random.randint(0, 3)
                sessions.append(
                    (
                        training_type,
                        float(hold_time),
                        1,
                        json.dumps(
                            {
                                "hold_time": hold_time,
                                "contraction_count": contractions,
                            }
                        ),
                        1,
                        completed_at,
                    )
                )
            elif training_type == "o2":
                # O2: 8 rounds, hold 60-120s, total ~8-16 min
                hold = random.randint(60, 120)
                total = hold * 8 + random.randint(60, 180)  # holds + rests
                sessions.append(
                    (
                        training_type,
                        float(total),
                        8,
                        json.dumps(
                            {
                                "total_rounds": 8,
                                "hold_time": hold,
                                "initial_rest_time": 120,
                                "rest_decrement": 15,
                            }
                        ),
                        1,
                        completed_at,
                    )
                )
            else:  # co2
                # CO2: 8 rounds, initial hold 60-90s, total ~8-14 min
                initial_hold = random.randint(60, 90)
                total = initial_hold * 8 + 15 * 28 + random.randint(30, 120)
                sessions.append(
                    (
                        training_type,
                        float(total),
                        8,
                        json.dumps(
                            {
                                "total_rounds": 8,
                                "initial_hold_time": initial_hold,
                                "hold_increment": 15,
                                "rest_time": 120,
                            }
                        ),
                        1,
                        completed_at,
                    )
                )

    # Also add a couple of sessions for today so the heatmap shows today
    for training_type in ["o2", "co2"]:
        hour = 8 if training_type == "o2" else 19
        completed_at = today.replace(hour=hour, minute=30, second=0).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        hold = random.randint(70, 110)
        total = hold * 8 + random.randint(80, 160)
        sessions.append(
            (
                training_type,
                float(total),
                8,
                json.dumps({"total_rounds": 8, "hold_time": hold}),
                1,
                completed_at,
            )
        )

    try:
        conn.executemany(
            """
            INSERT INTO practice_sessions
            (training_type, duration_seconds, rounds_completed,
             parameters, completed, completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            sessions,
        )
        conn.commit()
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Generate Apno store listing screenshots"
    )
    parser.add_argument(
        "--device",
        choices=["phone", "tablet", "all"],
        default="all",
        help="Device to generate screenshots for (default: all)",
    )
    parser.add_argument(
        "--_run-device",
        dest="run_device",
        help=argparse.SUPPRESS,  # internal: run a single device in-process
    )
    args = parser.parse_args()

    # Internal: called by subprocess to generate for a single device
    if args.run_device:
        parts = args.run_device.split(",")
        name, w, h, density = parts[0], int(parts[1]), int(parts[2]), parts[3]
        output_dir = PROJECT_ROOT / "screenshots" / name
        _generate_device(name, w, h, density, output_dir)
        return 0

    # Seed the database once before generating any screenshots
    _seed_database()

    devices = {
        "phone": [("phone", 1080, 1920, "3")],
        "tablet": [("tablet", 1920, 2560, "2")],
        "all": [("phone", 1080, 1920, "3"), ("tablet", 1920, 2560, "2")],
    }

    base_dir = PROJECT_ROOT / "screenshots"
    device_list = devices[args.device]

    for device_name, width, height, density in device_list:
        print(f"\n{'=' * 60}")
        print(
            f"Generating screenshots for {device_name}"
            f" ({width}x{height}, density={density})"
        )
        print(f"{'=' * 60}\n")

        # Spawn a subprocess for each device so Kivy gets a fresh
        # initialization with the correct density/DPI env vars.
        env = os.environ.copy()
        env["KIVY_LOG_MODE"] = "PYTHON"
        env["KIVY_NO_ARGS"] = "1"
        env["KIVY_LOG_LEVEL"] = "warning"
        env["KIVY_METRICS_DENSITY"] = density
        env["KIVY_DPI"] = str(int(density) * 160)

        result = subprocess.run(
            [
                sys.executable,
                __file__,
                "--_run-device",
                f"{device_name},{width},{height},{density}",
            ],
            env=env,
            cwd=str(PROJECT_ROOT),
        )
        if result.returncode != 0:
            print(f"  ERROR: Failed for {device_name}")
            return 1

        print(f"\n  Screenshots saved to: {base_dir / device_name}")

    print(f"\n{'=' * 60}")
    print("All screenshots generated successfully!")
    print(f"Location: {base_dir}")
    print(f"{'=' * 60}")
    return 0


def _capture(window, filepath):
    """Capture screenshot and fix the filename.

    Window.screenshot() appends a counter suffix like '0001'.
    We find the actual file and rename it.
    """
    actual = window.screenshot(name=filepath)
    if actual and actual != filepath:
        actual_path = Path(actual)
        target_path = Path(filepath)
        if actual_path.exists():
            if target_path.exists():
                target_path.unlink()
            actual_path.rename(target_path)


def _generate_device(device_name, width, height, density, output_dir):
    """Generate all screenshots for a single device.

    This runs in a subprocess with KIVY_METRICS_DENSITY already set,
    so dp() and sp() values scale correctly for the target device.
    """
    from kivy.config import Config

    Config.set("graphics", "width", str(width))
    Config.set("graphics", "height", str(height))
    Config.set("graphics", "resizable", "0")

    from kivy.animation import Animation
    from kivy.base import EventLoop
    from kivy.clock import Clock
    from kivy.core.window import Window

    Window.size = (width, height)

    sys.path.insert(0, str(PROJECT_ROOT))
    from apno.app import Apno

    app = Apno()
    app._run_prepare()

    Window.size = (width, height)

    sm = app.root.ids.screen_manager
    sm.transition.duration = 0

    def tick(n=10):
        for _ in range(n):
            EventLoop.idle()
            Clock.tick()
            Animation.cancel_all(sm)

    tick(20)
    Window.size = (width, height)
    tick(10)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Clean existing screenshots
    for f in output_dir.glob("*.png"):
        f.unlink()

    def take(filename, screen_name, title, setup_fn=None):
        app.change_screen(screen_name, title)
        tick(15)

        if setup_fn:
            screen = sm.get_screen(screen_name)
            setup_fn(screen)
            tick(15)

        filepath = str(output_dir / filename)
        _capture(Window, filepath)
        print(f"  {filename}")

    # Capture each screenshot
    take("home_1.png", "home", "Apno")
    take("o2_1.png", "o2_screen", "O2 Tables")
    take("o2_2.png", "o2_screen", "O2 Tables", _setup_o2_running)
    sm.get_screen("o2_screen").reset_training()
    tick(10)
    take("co2_1.png", "co2_screen", "CO2 Tables")
    take("co2_2.png", "co2_screen", "CO2 Tables", _setup_co2_running)
    sm.get_screen("co2_screen").reset_training()
    tick(10)
    take("free_1.png", "free_screen", "Free Training")
    take("free_2.png", "free_screen", "Free Training", _setup_free_running)
    sm.get_screen("free_screen").reset_session()
    tick(10)
    take("history_1.png", "history_screen", "Training History")
    take("home_2.png", "home", "Apno")

    app.stop()


# ---------------------------------------------------------------------------
# Setup helpers
# ---------------------------------------------------------------------------


def _setup_o2_running(screen):
    screen.current_round = 3
    screen.phase_text = "Hold"
    screen.phase_color = [0.25, 0.45, 0.85, 1]
    screen.time_text = "01:12"
    screen.instruction_text = "Hold your breath - stay relaxed"
    screen.is_running = True
    pc = screen.ids.progress_circle
    pc.progress_color = [0.25, 0.45, 0.85, 1]
    pc.progress = 40


def _setup_co2_running(screen):
    screen.current_round = 5
    screen.phase_text = "Hold"
    screen.phase_color = [1.0, 0.7, 0.2, 1]
    screen.time_text = "00:42"
    screen.instruction_text = "Hold your breath - stay relaxed"
    screen.hold_info_text = "Stay relaxed, you've got this!"
    screen.is_running = True
    pc = screen.ids.progress_circle
    pc.progress_color = [1.0, 0.7, 0.2, 1]
    pc.progress = 55


def _setup_free_running(screen):
    screen.hold_count = 2
    screen.phase_text = "Holding..."
    screen.phase_color = [0.9, 0.3, 0.3, 1]
    screen.time_text = "01:34"
    screen.instruction_text = "Tap anywhere on the timer when you feel a contraction"
    screen.button_text = "Stop"
    screen.is_holding = True
    screen.contraction_count = 2
    screen.best_time_text = "Session: 02:15"
    screen.alltime_best_text = "All-time: 03:22"
    pc = screen.ids.progress_circle
    pc.progress_color = [0.9, 0.3, 0.3, 1]
    pc.progress = 52


if __name__ == "__main__":
    sys.exit(main())
