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


# TODO !!!!!!!!!!!!!!
class TrackerConfig(BaseModel):
    # serial: str
    address: str = "None"
    vibration_multiplier: float = 1.0
    pattern_override: str = "None"
    battery_threshold: int = 20


class PatternConfig(BaseModel):
    pattern: str = "Linear"
    str_min: int = 20
    str_max: int = 80
    speed: int = 1

    def __init__(self, pattern: str, str_min: int, str_max: int, speed: int, **data: Any):
        super().__init__(**data)
        self.pattern = pattern
        self.str_min = str_min
        self.str_max = str_max
        self.speed = int(speed)


class AppConfig(BaseModel):
    version: int = 1
    osc_address: str = "127.0.0.1"
    # osc_port: int = 9000
    osc_receiver_port: int = 9001
    tracker_to_osc: Dict[str, str] = {}  # TODO Remove in favor of tracker_dict
    tracker_to_vib_int_override: Dict[str, float] = {}  # TODO Remove in favor of tracker_dict
    pattern_config_list: List[PatternConfig] = []
    tracker_config_dict: Dict[str, TrackerConfig] = {}

    def get_multiplier(self, tracker_serial):
        return self.tracker_to_vib_int_override[tracker_serial]\
            if tracker_serial in self.tracker_to_vib_int_override else 1.0

    def check_integrity(self):
        if len(self.pattern_config_list) != 2:
            self.init_pattern_config()

    def init_pattern_config(self):
        self.pattern_config_list.clear()
        # PROXIMITY Defaults: (Linear, 50, 4)
        from BridgeApp.app_pattern import VibrationPattern
        self.pattern_config_list.append(PatternConfig(VibrationPattern.VIB_PATTERN_LIST[2], 40, 80, 4))
        # VELOCITY Defaults: (None, 80, 32)
        self.pattern_config_list.append(PatternConfig(VibrationPattern.VIB_PATTERN_LIST[0], 40, 80, 32))

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
