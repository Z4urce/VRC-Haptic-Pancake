import os.path
import json
from pydantic import BaseModel
from typing import Dict

CONFIG_FILE_NAME: str = "config.json"


class VRTracker:
    index: int
    model: str
    serial: str

    def __init__(self, index: int, model: str, serial: str):
        self.index = index
        self.model = model
        self.serial = serial


class AppConfig(BaseModel):
    version: int = 1
    osc_address: str = "127.0.0.1"
    osc_port: int = 9000
    osc_receiver_port: int = 9001
    tracker_to_osc: Dict[str, str] = {}
    vibration_intensity: int = 400

    @staticmethod
    def load():
        # return AppConfig()
        if not os.path.exists(CONFIG_FILE_NAME):
            return AppConfig()
        with open(CONFIG_FILE_NAME, "r") as settings_file:
            return AppConfig(**json.load(settings_file))

    def save(self):
        # print("Emulating save...")
        with open(CONFIG_FILE_NAME, "w+") as settings_file:
            json.dump(self.model_dump(), fp=settings_file)
