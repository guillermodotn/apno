# Apno

<p align="center">
  <img src="apno/assets/images/logo.svg" alt="Apno Logo" width="200">
</p>

A cross-platform apnea and breath-holding training app built with Python and Kivy.

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Python Kivy](https://img.shields.io/badge/Python-Kivy-555555?logo=python&logoColor=white&labelColor=555555&color=8b5cf6)](https://kivy.org/)

## Features

- **O2 Tables** - Fixed hold time with decreasing rest periods to improve oxygen efficiency
- **CO2 Tables** - Increasing hold time with fixed rest periods to build CO2 tolerance
- **Free Training** - Practice breath holds at your own pace with a simple timer
- **Customizable Settings** - Adjust hold times, rest periods, and number of rounds
- **Visual Progress** - Animated progress circle with phase-based color feedback

## Development

### Setup

```bash
# Install development dependencies
uv sync --group dev

# Install pre-commit hooks
uv run pre-commit install
```

### Running in Development Mode

Development mode stores the database in the project directory instead of the system data directory:

```bash
uv run --env-file .env.development apno
```

Or set the environment variable manually:

```bash
APNO_DEV=1 uv run apno
```

### Code quality

```bash
uv run ruff check .
```

```bash
uv run ruff format .
```

### Versioning

The single source of truth for the app version is `apno/__init__.py`:

```python
__version__ = "0.2.0"
```

The version script updates all files that reference it (`apno/__init__.py`,
`pyproject.toml`, `buildozer.spec`):

```bash
# Get current version
python scripts/version.py get

# Set a specific version
python scripts/version.py set 0.3.0

# Bump patch/minor/major
python scripts/version.py bump patch
python scripts/version.py bump minor
python scripts/version.py bump major
```

After bumping, run `uv lock` to sync the lockfile.

