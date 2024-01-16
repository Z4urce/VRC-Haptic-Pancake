from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from config import AppConfig
import threading


class VRChatOSCReceiver:
    def __init__(self, config: AppConfig, param_received_event):
        self.thread = None
        self.server = None
        self.config = config
        self.dispatcher = Dispatcher()
        self.param_received_event = param_received_event

    def shutdown(self):
        if self.is_alive():
            print("[OSC] Shutting down...")
            self.server.shutdown()
            self.thread.join()
            print("[OSC] Shutdown completed.")

    def event_received(self, address, osc_value):
        if type(osc_value) != float: return
        self.param_received_event(address, osc_value)

    def run(self):
        if not self.is_alive(): return
        self.dispatcher.map("/avatar/parameters/*", self.event_received)
        print(f"[OSC] VRChatOSCReceiver serving on {self.server.server_address}")
        self.server.serve_forever()

    def is_alive(self):
        return self.server is not None

    def start_server(self):
        try:
            address = (self.config.osc_address, int(self.config.osc_receiver_port))
            self.server = osc_server.OSCUDPServer(address, self.dispatcher)
        except:
            print(f"[OSC][ERROR] Port: {self.config.osc_receiver_port} occupied.")
            return

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def restart_server(self):
        self.shutdown()
        self.start_server()
