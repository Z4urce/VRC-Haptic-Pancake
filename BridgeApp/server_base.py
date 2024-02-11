from app_config import AppConfig


class ServerBase:
    def __init__(self, config: AppConfig, param_received_event, status_update):
        self.config = config
        self.param_received_event = param_received_event
        self.status_update = status_update

    def restart_server(self):
        raise NotImplementedError("Subclass must implement abstract method: restart_server")

    def shutdown(self):
        raise NotImplementedError("Subclass must implement abstract method: shutdown")
