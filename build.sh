#!/bin/bash
# See http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

# Build Haptic Pancake bridge app on Linux
#
# NOTE: If changing this, make sure "build.bat" is also updated!

# Build and activate a Python virtual environment to keep your system clean
if [ ! -d "ignored-hpb-venv" ]; then
    python3 -m venv "ignored-hpb-venv"
fi
source "ignored-hpb-venv/bin/activate"

# Install/update Haptic Pancake dependencies
pip3 install -r "BridgeApp/requirements.txt"

# Add PyInstaller
pip3 install pyinstaller

pyinstaller -wF --collect-all openvr --name hapticpancake_linux --icon=Images\icon.ico BridgeApp/main.py
# "hapticpancake.spec"

# Spec files don't need to stick around if you're generating them with a script
# and not modifying the result
rm "hapticpancake_linux.spec"

echo
echo "--------------------------------"
echo "Result: dist/hapticpancake_linux"
echo "--------------------------------"
