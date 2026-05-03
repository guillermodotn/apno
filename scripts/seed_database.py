#!/usr/bin/env python3
"""Populate the database with sample training sessions.

Creates a realistic training history for development and testing.
Can be used standalone or imported by other scripts.

Usage:
    uv run --env-file .env.development python scripts/seed_database.py
    uv run --env-file .env.development python scripts/seed_database.py --days 60
    uv run --env-file .env.development python scripts/seed_database.py --clear
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Prevent Kivy from intercepting command-line arguments
os.environ["KIVY_NO_ARGS"] = "1"

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from apno.utils.database import get_connection, init_db  # noqa: E402


def seed_database(days=30, seed=42, clear=False):
    """Insert sample training sessions spread across the past N days.

    Creates a realistic training history with sessions on ~2/3 of the
    days so the heatmap looks populated. Durations are kept realistic
    (hold times between 60-120s, session totals between 8-16 minutes).

    Args:
        days: Number of past days to generate sessions for.
        seed: Random seed for reproducible data.
        clear: If True, delete existing sessions before inserting.
    """
    init_db()
    conn = get_connection()

    if clear:
        conn.execute("DELETE FROM practice_sessions")
        conn.execute("DELETE FROM contractions")
        conn.commit()

    random.seed(seed)
    today = datetime.now()

    # Pick ~2/3 of the days to have sessions on
    num_training_days = int(days * 2 / 3)
    training_days = sorted(
        random.sample(range(1, days + 1), min(num_training_days, days)),
        reverse=True,
    )

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
            hour = random.choice([7, 8, 9, 18, 19, 20])
            minute = random.randint(0, 45)
            ts = day.replace(hour=hour + i, minute=minute, second=0)
            completed_at = ts.strftime("%Y-%m-%d %H:%M:%S")

            if training_type == "free":
                hold_time = random.randint(60, 115)
                contraction_count = random.randint(0, 4)
                # Generate realistic contraction times (typically in last 40% of hold)
                contraction_times = sorted(
                    random.uniform(hold_time * 0.6, hold_time - 2)
                    for _ in range(contraction_count)
                )
                sessions.append(
                    (
                        training_type,
                        float(hold_time),
                        1,
                        json.dumps(
                            {
                                "hold_time": hold_time,
                                "contraction_count": contraction_count,
                            }
                        ),
                        1,
                        completed_at,
                        contraction_times,
                    )
                )
            elif training_type == "o2":
                hold = random.randint(60, 120)
                total = hold * 8 + random.randint(60, 180)
                sessions.append(
                    (
                        training_type,
                        float(total),
                        8,
                        json.dumps(
                            {
                                "total_rounds": 8,
                                "hold_time": hold,
                                "initial_breathe_time": 120,
                                "breathe_decrement": 10,
                            }
                        ),
                        1,
                        completed_at,
                    )
                )
            else:  # co2
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
                                "hold_increment": 10,
                                "breathe_time": 120,
                            }
                        ),
                        1,
                        completed_at,
                    )
                )

    # Add sessions for today so the heatmap shows today
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
        contraction_count = 0
        for session in sessions:
            # Extract contraction times if present (free training only)
            contraction_times = session[6] if len(session) > 6 else []
            session_data = session[:6]

            cursor = conn.execute(
                """
                INSERT INTO practice_sessions
                (training_type, duration_seconds, rounds_completed,
                 parameters, completed, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                session_data,
            )

            # Insert contraction records
            if contraction_times:
                session_id = cursor.lastrowid
                for seconds in contraction_times:
                    conn.execute(
                        """
                        INSERT INTO contractions
                        (session_id, seconds_into_hold)
                        VALUES (?, ?)
                        """,
                        (session_id, round(seconds, 1)),
                    )
                    contraction_count += 1

        conn.commit()
        print(
            f"Inserted {len(sessions)} sessions "
            f"and {contraction_count} contractions over {days} days"
        )
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Populate the Apno database with sample training data"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of past days to generate sessions for (default: 30)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible data (default: 42)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing sessions before inserting",
    )
    args = parser.parse_args()

    seed_database(days=args.days, seed=args.seed, clear=args.clear)


if __name__ == "__main__":
    main()
