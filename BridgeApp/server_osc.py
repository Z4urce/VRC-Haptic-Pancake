from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from server_base import ServerBase
from app_config import AppConfig
import threading


class VRChatOSCReceiver(ServerBase):
    def __init__(self, config: AppConfig, param_received_event, status_update):
        super().__init__(config, param_received_event, status_update)
        self.thread = None
        self.server = None
        self.dispatcher = Dispatcher()

    def shutdown(self):
        if self.is_alive():
            self.print_status("Shutting down...", True)
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
            self.print_status("Shutdown completed.")

    def event_received(self, address, osc_value):
        try:
            float_value = float(osc_value)
            self.param_received_event(address, float_value)
        except ValueError:
            pass

    def run(self):
        if not self.is_alive():
            return
        self.dispatcher.map("/avatar/parameters/*", self.event_received)
        self.print_status(f"OSC Receiver serving on {self.server.server_address}", True)
        self.server.serve_forever()

    def is_alive(self):
        return self.server is not None

    def start_server(self):
        try:
            address = (self.config.server_ip, int(self.config.server_port))
            self.server = osc_server.OSCUDPServer(address, self.dispatcher)
        except Exception as e:
            self.print_status(f"[ERROR] Port: {self.config.server_port} occupied.\n{e}", True, True)
            return

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def restart_server(self):
        self.print_status("Restarting...", True)
        self.shutdown()
        self.start_server()

    def print_status(self, text, update_status_bar=False, is_error=False):
        print(f"[OSC] {text}")
        if update_status_bar:
            self.status_update(text, is_error)
