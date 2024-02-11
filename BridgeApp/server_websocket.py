from server_base import ServerBase
from app_config import AppConfig
import time
import json
import websockets.sync.server
import threading


class ResoniteWebSocketServer(ServerBase):
    def __init__(self, config: AppConfig, param_received_event, status_update):
        super().__init__(config, param_received_event, status_update)
        self.thread = None
        self.server = None
        self.close = False

    def message_received(self, websocket):
        for message in websocket:
            # self.print_status(f"Message received: {message}")
            try:
                message_dict = json.loads(message)
                for key, value in message_dict.items():
                    self.param_received_event(key, value)
            except json.decoder.JSONDecodeError:
                pass

    def thread_main(self):
        self.print_status(f"WebSocket server running at {self.config.server_ip}:{self.config.server_port}", True)
        try:
            self.server.serve_forever()
        except OSError as e:
            self.print_status(f"[Error] Port {self.config.server_port} is occupied.", True, True)
            print(e)
        self.print_status("Thread ended.")

    def start_server(self):
        self.print_status("Creating thread.")
        self.server = websockets.sync.server.serve(self.message_received, self.config.server_ip, self.config.server_port)
        self.thread = threading.Thread(target=self.thread_main)
        self.thread.start()

    def shutdown(self):
        self.print_status("Shutting down...", True)
        if self.server is not None:
            self.server.shutdown()
        if self.thread is not None:
            self.thread.join()
        self.print_status("Shutdown completed.")

    def restart_server(self):
        self.print_status("Restarting...", True)
        self.shutdown()
        self.start_server()

    def print_status(self, text, update_status_bar=False, is_error=False):
        print(f"[WebSocket] {text}")
        if update_status_bar:
            self.status_update(text, is_error)
