---
title: "Changelog"
description: "Release history for Apno"
---

## v0.3.0

### Features

- Audio feedback with sonar-style tones during training (countdown, hold, breathe, session complete)
- Session detail screen with hold time, date, status, and contraction timeline
- JSON data export from settings
- Auto-configure training tables from personal best hold time
- History accessible from navigation drawer
- Trophy icon for personal best free training hold
- Keep screen on during training sessions
- Sound and screen wake-lock toggles in settings

### Improvements

- Correct O2/CO2 table naming to match freediving terminology
- Simplified 2-phase training cycle (breathe and hold, no separate rest phase)
- Beginner-friendly default training settings
- Per-training round configuration (separate for CO2 and O2 tables)
- Completed vs incomplete sessions visually distinguished in history
- Redesigned splash screen with app logo and tagline
- Toast notifications for export feedback

### Fixes

- Fix streak text showing "0 day streak" instead of "No streak"
- Fix text clipping in about screen link cards
- Fix Unicode symbols not rendering on Android
- Fix settings not persisting across app restarts
- Fix settings not propagating to training screens on startup

---

## v0.2.1

### Fixes

- Fix status bar overlapping the app content
- Fix app not showing as compatible on some devices

### Improvements

- Show app logo on splash screen

---

## v0.2.0

### Features

- Free training contraction tracking
- Day streak tracking
- Training session history
- Session heatmap calendar
- All-time best records with persistence
- Settings screen
- Website and GitHub links in about page

### Improvements

- Navy blue color theme
- Progress circle color feedback
- Back button no longer exits the app

---

## v0.1.0

Initial release.

### Features

- O2 table training with decreasing rest intervals
- CO2 table training with increasing hold times
- Free training mode with contraction tracking
- Animated progress circle with phase-based color feedback
- Session history with heatmap calendar
- Customizable hold times, rest periods, and round counts
