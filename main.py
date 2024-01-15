import traceback
import platform
from osc import VRChatOSCReceiver
from config import AppConfig
from tracker import OpenVRTracker
from gui import GUIRenderer

vr: OpenVRTracker = None
osc_receiver: VRChatOSCReceiver = None
config: AppConfig = None


def main():
    print(f"Using Python: {platform.python_version()}")
    print("Starting up...")
    # Load the config
    global config
    config = AppConfig.load()
    config.save()
    print("Config loaded")

    # Start the OSC receiver thread
    global osc_receiver
    osc_receiver = VRChatOSCReceiver(config, param_received)
    osc_receiver.start_server()
    print("OSC receiver started")

    # Init GUI
    gui = GUIRenderer(config, pulse_test, restart_osc_server)
    print("GUI initialized")

    # Init OpenVR
    global vr
    vr = OpenVRTracker()

    print("OpenVR initialized" if vr.is_alive() else "OpenVR is not alive")

    # Report errors to GUI is any exists
    if not osc_receiver.is_alive():
        gui.add_message("Could not start OSC receiver. The selected port may be occupied.")
    if not vr.is_alive():
        gui.add_message("Could not connect to Steam VR. Please restart the app.")
    elif len(vr.devices) == 0:
        gui.add_message("No active trackers has been detected. Please restart the app.")

    # Add trackers to GUI
    for device in vr.devices:
        gui.add_tracker(device.index, device.serial, device.model)
    print("GUI Updated")

    # Main GUI loop here
    while gui.run(): pass


# Adapter functions
def pulse_test(id):
    vr.pulse(id, config.vibration_intensity)


def restart_osc_server():
    if osc_receiver is not None:
        osc_receiver.restart_server()


def param_received(address, value):
    for key in config.tracker_to_osc.keys():
        if config.tracker_to_osc[key] == address:
            vr.pulse_by_serial(key, int(value * config.vibration_intensity))


if __name__ == '__main__':
    try:
        main()
        if config is not None: config.save()
    except Exception as e:
        print(f"Main Error:\n{traceback.format_exc()}")
    finally:
        # Shut down the processes
        print("Halting...")
        if vr is not None: vr.shutdown()
        if osc_receiver is not None: osc_receiver.shutdown()
