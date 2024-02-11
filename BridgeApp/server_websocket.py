import time

from server_base import ServerBase
from app_config import AppConfig
import json
import asyncio
import websockets
import threading


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ResoniteWebSocketServer(ServerBase):
    def __init__(self, config: AppConfig, param_received_event, status_update):
        super().__init__(config, param_received_event, status_update)
        self.thread = None
        self.server = None
        self.loop = None
        self.close = False

    async def message_received(self, websocket):
        async for message in websocket:
            self.print_status(f"Message received: {message}")
            try:
                message_dict = json.loads(message)
                for key, value in message_dict.items():
                    self.param_received_event(key, value)
            except json.decoder.JSONDecodeError:
                pass

    def thread_main(self):
        self.print_status(f"WebSocket server running at {self.config.server_ip}:{self.config.server_port}", True)
        try:
            self.loop.run_until_complete(self.server)
            self.loop.run_forever()
            self.loop.close()
        except OSError as e:
            self.print_status(f"[Error] Port {self.config.server_port} is occupied.", True, True)
            print(e)
        self.print_status("Thread ended.")

    def start_server(self):
        self.print_status("Creating thread.")
        self.loop = asyncio.new_event_loop()
        self.server = websockets.serve(self.message_received, self.config.server_ip, self.config.server_port, loop=self.loop)
        self.thread = threading.Thread(target=self.thread_main)
        self.thread.start()

    def shutdown(self):
        if self.loop is not None and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.loop.call_soon_threadsafe(self.loop.close)
        if self.thread is not None:
            self.thread.join()

        time.sleep(.5)
        try:
            tasks = asyncio.all_tasks()
            for task in tasks:
                task.cancel()
        except RuntimeError:
            pass

        self.print_status("Shutdown completed.")

    def restart_server(self):
        self.print_status("Restarting...", True)
        self.shutdown()
        self.start_server()

    def print_status(self, text, update_status_bar=False, is_error=False):
        print(f"{bcolors.WARNING}[WebSocket] {text}{bcolors.ENDC}")
        if update_status_bar:
            self.status_update(text, is_error)
