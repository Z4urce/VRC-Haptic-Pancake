from app_config import AppConfig
from app_gui import GUIRenderer
from server_base import ServerBase
from server_osc import VRChatOSCReceiver
from server_websocket import ResoniteWebSocketServer
from target_ovr import OpenVRTracker
import traceback
import platform

bridge_server: ServerBase = None
vr: OpenVRTracker = None
config: AppConfig = None
gui: GUIRenderer = None

supported_models = ["VIVE Tracker 3.0 MV"]

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
    gui = GUIRenderer(config, pulse_test, restart_bridge_server, refresh_tracker_list)
    print("[Main] GUI initialized")

    # Start the Server
    start_bridge_server()

    print("[Main] Bridge server started")

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


def start_bridge_server():
    global bridge_server
    if config.server_type == 1:
        bridge_server = ResoniteWebSocketServer(config, param_received, gui.update_osc_status_bar)
    else:
        bridge_server = VRChatOSCReceiver(config, param_received, gui.update_osc_status_bar)
    bridge_server.start_server()


# Adapter functions
def pulse_test(tracker_serial):
    print(f"[Main] Pulse test for {tracker_serial} executed.")
    vr.pulse_by_serial(tracker_serial, 500)
    # param_received("TEST", 1.0)


def restart_bridge_server():
    if bridge_server is not None:
        bridge_server.shutdown()
    start_bridge_server()


def refresh_tracker_list():
    if vr is None or gui is None:
        return

    for device in vr.query_devices():
        if device.model not in supported_models:
            continue
        gui.add_tracker(device.index, device.serial, device.model)

    # Debug tracker (Uncomment this for debug purposes)
    # gui.add_tracker(99, "T35T-53R1AL", "Test Model 1.0")
    print("[Main] Tracker list refreshed")


def param_received(address, value):
    # value is the floating value (0..1) that determines how intense the feedback should be
    for serial, tracker_config in config.tracker_config_dict.items():
        if tracker_config.address == address:
            vr.set_strength(serial, value)


if __name__ == '__main__':
    try:
        main()
        if config is not None:
            config.save()
    except Exception as e:
        print(f"[Main][ERROR] {e}\n{traceback.format_exc()}")
        with open('hpb_crashlog.txt', "w+") as crash_log:
            import json
            json.dump(traceback.format_exc(), fp=crash_log)
    finally:
        # Shut down the processes
        print("[Main] Halting...")
        if bridge_server is not None:
            bridge_server.shutdown()
