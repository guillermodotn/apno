"""Generate sonar-style sound effects for Apno.

Generates 5 WAV files used as audio feedback during training sessions:
- countdown_tick.wav  — short blip played each second before hold
- hold_start.wav      — sustained tone signaling hold phase begins
- rest_start.wav      — low deep ping signaling rest/breathe phase
- session_complete.wav — triple ascending pings signaling session end
- contraction_tap.wav — quick click for contraction acknowledgment

All sounds use pure sine waves with exponential decay, generated with
Python stdlib only (wave, struct, math). No external dependencies.

Usage:
    python scripts/generate_sounds.py
"""

import math
import os
import struct
import wave

SAMPLE_RATE = 44100
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "apno", "assets", "sounds")


def generate_tone(
    frequency: float,
    duration: float,
    decay: float = 5.0,
    volume: float = 0.7,
    freq_sweep: float = 0.0,
) -> list[float]:
    """Generate a sine wave tone with exponential decay.

    Args:
        frequency: Base frequency in Hz.
        duration: Duration in seconds.
        decay: Exponential decay rate (higher = faster fade).
        volume: Peak amplitude (0.0 to 1.0).
        freq_sweep: Frequency drift per second in Hz (negative = downward).
    """
    samples = []
    n_samples = int(SAMPLE_RATE * duration)
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        envelope = math.exp(-decay * t) * volume
        freq = frequency + freq_sweep * t
        sample = envelope * math.sin(2 * math.pi * freq * t)
        samples.append(sample)
    return samples


def save_wav(filepath: str, samples: list[float]):
    """Save audio samples to a 16-bit mono WAV file."""
    with wave.open(filepath, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            packed = struct.pack("<h", int(clamped * 32767))
            wav.writeframes(packed)
    print(f"  {filepath}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating sounds...\n")

    # Countdown tick: subtle blip at 900Hz, moderate decay
    save_wav(
        os.path.join(OUTPUT_DIR, "countdown_tick.wav"),
        generate_tone(900, 0.15, decay=8, volume=0.4, freq_sweep=-50),
    )

    # Hold start: same 900Hz tone, sustained with minimal decay
    save_wav(
        os.path.join(OUTPUT_DIR, "hold_start.wav"),
        generate_tone(900, 0.4, decay=0.5, volume=0.7, freq_sweep=-50),
    )

    # Breathe start: low 500Hz ping with long lingering decay
    save_wav(
        os.path.join(OUTPUT_DIR, "breathe_start.wav"),
        generate_tone(500, 0.8, decay=2, volume=0.7, freq_sweep=-15),
    )

    # Session complete: three ascending pings (600, 750, 900 Hz)
    session = []
    for freq in [600, 750, 900]:
        ping = generate_tone(freq, 0.2, decay=6, volume=0.7, freq_sweep=-30)
        session.extend(ping)
        session.extend([0.0] * int(SAMPLE_RATE * 0.15))
    save_wav(os.path.join(OUTPUT_DIR, "session_complete.wav"), session)

    # Contraction tap: short high click at 1000Hz
    save_wav(
        os.path.join(OUTPUT_DIR, "contraction_tap.wav"),
        generate_tone(1000, 0.08, decay=15, volume=0.5, freq_sweep=-100),
    )

    print(f"\nDone! Files saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
