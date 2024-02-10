from app_config import AppConfig
import json
import asyncio
import websockets


class ResoniteWebSocketServer:
    def __init__(self, config: AppConfig, param_received_event, status_update):
        self.stop_event = asyncio.Event()
        self.config = config
        self.param_received_event = param_received_event
        self.status_update = status_update
        self.server = None
        self.future = None

    async def run(self, websocket):
        self.print_status(f"Serving...{self.server}", True)
        while not self.stop_event.is_set():
            message = await websocket.recv()
            message_dict = json.loads(message)
            for key, value in message_dict.items():
                self.param_received_event(key, value)

    # Example usage:
    async def main(self):
        try:
            async with websockets.serve(self.run, self.config.osc_address, self.config.osc_receiver_port) as self.server:
                self.print_status(f"Server type: {self.server}")
                self.future = await asyncio.Future()  # run forever
        except Exception as e:
            self.print_status(f"[ERROR] {e}", True, True)

    def start_server(self):
        asyncio.run(self.main())

    def shutdown(self):
        self.stop_event.set()
        self.future.done()

    def restart_server(self):
        self.print_status("Restarting...", True)
        self.shutdown()
        self.start_server()

    def print_status(self, text, update_status_bar=False, is_error=False):
        print(f"[WebSocket] {text}")
        if update_status_bar:
            self.status_update(text, is_error)
