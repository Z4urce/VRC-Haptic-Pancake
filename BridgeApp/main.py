from app_config import AppConfig
from app_gui import GUIRenderer
from server_osc import VRChatOSCReceiver
from target_ovr import OpenVRTracker
import traceback
import platform

osc_receiver: VRChatOSCReceiver = None
vr: OpenVRTracker = None
config: AppConfig = None
gui: GUIRenderer = None


def main():
    print(f"[Main] Using Python: {platform.python_version()}")
    print("[Main] Starting up...")
    # Load the config
    global config
    config = AppConfig.load()
    config.check_integrity()
    config.save()
    print("[Main] Config loaded")

    # Init GUI
    global gui
    gui = GUIRenderer(config, pulse_test, restart_osc_server, refresh_tracker_list)
    print("[Main] GUI initialized")

    # Start the OSC receiver thread
    global osc_receiver
    osc_receiver = VRChatOSCReceiver(config, param_received, gui.update_osc_status_bar)
    osc_receiver.start_server()
    print("[Main] OSC receiver started")

    # Init OpenVR
    global vr
    vr = OpenVRTracker(config)

    # Add trackers to GUI
    refresh_tracker_list()

    # Add footer
    gui.add_footer()

    # Main GUI loop here
    while gui.run():
        pass


# Adapter functions
def pulse_test(tracker_id):
    print(f"[Main] Pulse test for {tracker_id} executed.")
    vr.pulse(tracker_id, 500)
    # param_received("TEST", 1.0)


def restart_osc_server():
    if osc_receiver is not None:
        osc_receiver.restart_server()


def refresh_tracker_list():
    if vr is None or gui is None:
        return

    for device in vr.query_devices():
        gui.add_tracker(device.index, device.serial, device.model)

    # Debug tracker (Uncomment this for debug purposes)
    gui.add_tracker(99, "T35T-53R1AL", "Test Model 1.0")
    print("[Main] Tracker list refreshed")


def param_received(osc_address, osc_value):
    # address is the OSC address
    # value is the floating value (0..1) that determines how intense the feedback should be
    for tracker_serial in config.tracker_to_osc.keys():
        if config.tracker_to_osc[tracker_serial] == osc_address:
            # This is a value between 0 and 1
            # vib_strength = vp.apply_pattern(tracker_serial, osc_value)

            # Apply the custom multiplier.
            # vib_strength *= config.tracker_to_vib_int_override[tracker_serial]\
            #     if tracker_serial in config.tracker_to_vib_int_override else 1.0

            vr.set_strength(tracker_serial, osc_value)


if __name__ == '__main__':
    try:
        main()
        if config is not None: config.save()
    except Exception as e:
        print(f"[Main][ERROR] {e}\n{traceback.format_exc()}")
    finally:
        # Shut down the processes
        print("[Main] Halting...")
        if osc_receiver is not None: osc_receiver.shutdown()
