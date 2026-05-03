"""Tests for the sound generation script."""

import importlib.util
import os
import struct
import wave
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "generate_sounds.py"


def _load_module():
    """Load generate_sounds.py as a module without __init__.py."""
    spec = importlib.util.spec_from_file_location("generate_sounds", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generate_sounds(tmp_path):
    """Test that generate_sounds.py creates valid WAV files."""
    gen = _load_module()

    original_dir = gen.OUTPUT_DIR
    gen.OUTPUT_DIR = str(tmp_path)

    try:
        gen.main()
    finally:
        gen.OUTPUT_DIR = original_dir

    expected_files = [
        "countdown_tick.wav",
        "hold_start.wav",
        "breathe_start.wav",
        "session_complete.wav",
        "contraction_tap.wav",
    ]

    for filename in expected_files:
        filepath = tmp_path / filename
        assert filepath.exists(), f"{filename} was not created"

        # Verify it's a valid WAV file
        with wave.open(str(filepath), "r") as wav:
            assert wav.getnchannels() == 1  # mono
            assert wav.getsampwidth() == 2  # 16-bit
            assert wav.getframerate() == 44100
            assert wav.getnframes() > 0


def test_generate_tone():
    """Test that generate_tone produces correct number of samples."""
    gen = _load_module()
    generate_tone = gen.generate_tone

    samples = generate_tone(440, 0.5, decay=5, volume=0.7)
    expected = int(44100 * 0.5)
    assert len(samples) == expected

    # All samples should be in [-1, 1] range
    assert all(-1.0 <= s <= 1.0 for s in samples)


def test_generate_tone_zero_duration():
    """Test that zero duration produces no samples."""
    generate_tone = _load_module().generate_tone

    samples = generate_tone(440, 0.0)
    assert len(samples) == 0


def test_save_wav(tmp_path):
    """Test saving samples to a WAV file."""
    save_wav = _load_module().save_wav

    samples = [0.5, -0.5, 0.0, 1.0, -1.0]
    filepath = str(tmp_path / "test.wav")
    save_wav(filepath, samples)

    assert os.path.exists(filepath)

    with wave.open(filepath, "r") as wav:
        assert wav.getnframes() == 5
        frames = wav.readframes(5)
        # Verify first sample (0.5 * 32767 = 16383)
        value = struct.unpack("<h", frames[:2])[0]
        assert value == 16383
