]

# Title of your application
title = Apno

# Package name
package.name = apno

# Package domain (used with package.name to create the package identifier)
package.domain = io.github.guillermodotn

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,jpeg,svg,ttf,kv,json

# Source files to exclude
source.exclude_exts = spec

# Directories to exclude
source.exclude_dirs = tests,.github,.venv,build,dist,__pycache__,.git,.ruff_cache,.buildozer,bin,scripts

# Application versioning
version = 0.2.0

# Application requirements (comma-separated)
requirements = python3,kivy==2.3.0,pillow

# Supported orientations (portrait, landscape, all)
orientation = portrait

# Enable fullscreen (hides Android status bar)
fullscreen = 1

# Permissions required by the app
# android.permissions = INTERNET

# Android API to use for the build
android.api = 35

# Minimum Android API level
android.minapi = 21

# Android NDK version
android.ndk = 25b

# Android architectures to build for (arm64 only, 99%+ of active devices)
android.archs = arm64-v8a

# Enable AndroidX support
android.enable_androidx = True

# Android app theme
android.apptheme = @android:style/Theme.NoTitleBar

# Presplash image and background color
presplash.filename = %(source.dir)s/apno/assets/images/logo.png
android.presplash_color = #FFFFFF

# Icon of the application (512x512 square)
icon.filename = %(source.dir)s/apno/assets/images/icon.png

# Release artifact type (aab for Play Store, apk for direct install)
android.release_artifact = aab

# Accept Android SDK license
android.accept_sdk_license = True

# Logcat filters (useful for debugging)
android.logcat_filters = *:S python:D

# Android keystore for signing release builds
android.keystore = release.keystore
android.keystorealias = apno

# Version code (overridden in CD with github.run_number + 200)
android.version.code = 201

[buildozer]

# Buildozer log level (0 = error, 1 = info, 2 = debug)
log_level = 2

# Display warning if buildozer is outdated
warn_on_root = 1

# Build directory
# build_dir = ./.buildozer

# Binary directory
# bin_dir = ./bin
