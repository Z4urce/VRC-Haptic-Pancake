REM Build Haptic Pancake bridge app on Linux
REM
REM NOTE: If changing this, make sure "build.sh" is also updated!
pyinstaller -wF --collect-all openvr --name hapticpancake --icon=Images\icon.ico BridgeApp/main.py
