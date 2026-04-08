#!/bin/bash
set -e

IMAGE_NAME="kivy/buildozer:latest"
CONTAINER_ENGINE="${CONTAINER_ENGINE:-podman}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root (parent of scripts dir)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}Using container engine: ${CONTAINER_ENGINE}${NC}"

# Create cache directories if they don't exist
mkdir -p "$HOME/.buildozer"
mkdir -p "$HOME/.android"

# Pull the image if not present
if ! $CONTAINER_ENGINE image exists "$IMAGE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}Pulling buildozer image...${NC}"
    $CONTAINER_ENGINE pull "$IMAGE_NAME"
fi

# Default command
CMD="${@:-android debug}"

echo -e "${GREEN}Running: buildozer ${CMD}${NC}"

# The kivy/buildozer container ships an old sdkmanager (2020) that can't
# install API 31+. Install modern cmdline-tools on the host if needed.
# These are cached in ~/.buildozer and mounted into the container.
SDK_DIR="$HOME/.buildozer/android/platform/android-sdk"
CMDLINE_TOOLS="$SDK_DIR/cmdline-tools/latest/bin/sdkmanager"

if [ ! -f "$CMDLINE_TOOLS" ]; then
    echo -e "${YELLOW}Installing modern Android SDK command-line tools...${NC}"
    TOOLS_URL="https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
    TOOLS_ZIP="$(mktemp)"
    curl -sL "$TOOLS_URL" -o "$TOOLS_ZIP"
    rm -rf "$SDK_DIR/cmdline-tools"
    mkdir -p "$SDK_DIR/cmdline-tools"
    unzip -qo "$TOOLS_ZIP" -d "$SDK_DIR/cmdline-tools"
    mv "$SDK_DIR/cmdline-tools/cmdline-tools" "$SDK_DIR/cmdline-tools/latest"
    rm -f "$TOOLS_ZIP"
    # Buildozer looks for sdkmanager at the old tools/bin path.
    # Copy the entire tools/bin directory since sdkmanager needs sibling files.
    rm -rf "$SDK_DIR/tools"
    mkdir -p "$SDK_DIR/tools/bin"
    cp -a "$SDK_DIR/cmdline-tools/latest/bin/"* "$SDK_DIR/tools/bin/"
    cp -a "$SDK_DIR/cmdline-tools/latest/lib" "$SDK_DIR/tools/"
    echo -e "${GREEN}SDK command-line tools installed${NC}"
fi

# Install required SDK platform if missing
API_LEVEL=$(grep "^android.api" "$PROJECT_DIR/buildozer.spec" | head -1 | tr -d ' ' | cut -d= -f2)
if [ ! -d "$SDK_DIR/platforms/android-${API_LEVEL}" ]; then
    echo -e "${YELLOW}Installing Android API ${API_LEVEL}...${NC}"
    yes | "$CMDLINE_TOOLS" --sdk_root="$SDK_DIR" --licenses > /dev/null 2>&1 || true
    "$CMDLINE_TOOLS" --sdk_root="$SDK_DIR" "platforms;android-${API_LEVEL}" "build-tools;${API_LEVEL}.0.0"
fi

# Detect TTY for interactive flag
TTY_FLAG=""
if [ -t 0 ]; then
    TTY_FLAG="-it"
fi

# Run the container
# - Mount project directory
# - Mount buildozer cache for faster rebuilds
# - BUILDOZER_WARN_ON_ROOT=0 skips the root warning prompt
# Note: kivy/buildozer image expects the command without 'buildozer' prefix
$CONTAINER_ENGINE run --rm $TTY_FLAG \
    -e BUILDOZER_WARN_ON_ROOT=0 \
    -v "$PROJECT_DIR:/home/user/hostcwd:Z" \
    -v "$HOME/.buildozer:/home/user/.buildozer:Z" \
    -v "$HOME/.android:/home/user/.android:Z" \
    "$IMAGE_NAME" \
    $CMD
