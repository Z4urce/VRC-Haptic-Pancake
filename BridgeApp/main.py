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
    print(f"[Main] Using Python: {platform.python_version()}")
    print("[Main] Starting up...")
    # Load the config
    global config
    config = AppConfig.load()
    config.save()
    print("[Main] Config loaded")

    # Start the OSC receiver thread
    global osc_receiver
    osc_receiver = VRChatOSCReceiver(config, param_received)
    osc_receiver.start_server()
    print("[Main] OSC receiver started")

    # Init GUI
    gui = GUIRenderer(config, pulse_test, restart_osc_server)
    print("[Main] GUI initialized")

    # Init OpenVR
    global vr
    vr = OpenVRTracker()

    print("[Main] OpenVR initialized" if vr.is_alive() else "[Main] OpenVR is not alive")

    # Add trackers to GUI
    for device in vr.devices:
        gui.add_tracker(device.index, device.serial, device.model)
    print("[Main] Trackers added")

    # Debug tracker
    gui.add_tracker(99, "T35T-53R1AL", "Test Model 1.0")

    # Report errors to GUI is any exists
    if not osc_receiver.is_alive():
        gui.add_message("Error: Could not start OSC receiver. The selected port may be occupied.")
    if not vr.is_alive():
        gui.add_message("Error: Could not connect to Steam VR. Please restart the app.")
    elif len(vr.devices) == 0:
        gui.add_message("Warning: No active trackers has been detected. Please restart the app.")

    # Add footer
    gui.add_footer()

    # Main GUI loop here
    while gui.run(): pass


# Adapter functions
def pulse_test(id):
    vr.pulse(id, 200)


def restart_osc_server():
    if osc_receiver is not None:
        osc_receiver.restart_server()


def param_received(address, value):
    # address is the OSC address
    # value is the floating value (0..1) that determines how intense the feedback should be
    for key in config.tracker_to_osc.keys():
        if config.tracker_to_osc[key] == address:
            vr.pulse_by_serial(key, int(value * config.global_vibration_intensity))


if __name__ == '__main__':
    try:
        main()
        if config is not None: config.save()
    except Exception as e:
        print(f"[Main][ERROR] {e}\n{traceback.format_exc()}")
    finally:
        # Shut down the processes
        print("[Main] Halting...")
        if vr is not None: vr.shutdown()
        if osc_receiver is not None: osc_receiver.shutdown()
