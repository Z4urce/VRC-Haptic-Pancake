import os.path
import json
from pydantic import BaseModel
from typing import Dict, List, Any

CONFIG_FILE_NAME: str = "config.json"


class VRTracker:  # Work in progress
    index: int
    model: str
    serial: str

    def __init__(self, index: int, model: str, serial: str):
        self.index = index
        self.model = model
        self.serial = serial


class TrackerVO(BaseModel):
    serial: str
    osc_address: str
    vibration_multiplier: float
    pattern_override: str


class PatternConfig(BaseModel):
    pattern: str = "Linear"
    intensity: int = 1
    speed: int = 1

    def __init__(self, pattern: str, intensity: int, speed: int, **data: Any):
        super().__init__(**data)
        self.pattern = pattern
        self.intensity = int(intensity)
        self.speed = int(speed)


class AppConfig(BaseModel):
    version: int = 1
    osc_address: str = "127.0.0.1"
    # osc_port: int = 9000
    osc_receiver_port: int = 9001
    tracker_to_osc: Dict[str, str] = {}  # TODO Remove in favor of tracker_dict
    tracker_to_vib_int_override: Dict[str, float] = {}  # TODO Remove in favor of tracker_dict
    pattern_config_list: List[PatternConfig] = []
    # tracker_dict: Dict[str, VRTracker] = {}
    # global_vibration_intensity: int = 100
    # global_vibration_cooldown: int = 100
    # global_vibration_pattern: str = "None"

    @staticmethod
    def load():
        # return AppConfig()
        if not os.path.exists(CONFIG_FILE_NAME):
            print("[Config] File not found. Loading default config...")
            return AppConfig()
        with open(CONFIG_FILE_NAME, "r") as settings_file:
            print(f"[Config] Opened {os.path.abspath(CONFIG_FILE_NAME)}")
            try:
                return AppConfig(**json.load(settings_file))
            except json.JSONDecodeError:
                print(f"[Config][ERROR] Corrupted file. Loading default config...")
                return AppConfig()

    def save(self):
        with open(CONFIG_FILE_NAME, "w+") as settings_file:
            json.dump(self.model_dump(), fp=settings_file)
