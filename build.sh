#!/bin/sh
# Build Haptic Pancake bridge app on Linux
#
# NOTE: If changing this, make sure "build.bat" is also updated!
pyinstaller -wF --collect-all openvr --name hapticpancake --icon=Images\icon.ico BridgeApp/main.py
