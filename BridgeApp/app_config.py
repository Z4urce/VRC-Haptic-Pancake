import os.path
import json
import mmap
import shutil
from pydantic import BaseModel
from typing import Dict, List, Any

CONFIG_FILE_NAME: str = "hapticpancake-config.json"

# Old versions of Haptic Pancake
LEGACY_CONFIG_FILE_NAME: str = "config.json"

# This is a runtime class for storing OVR trackers
class VRTracker:
    index: int
    model: str
    serial: str
    pulse_multiplier: float

    def __init__(self, index: int, model: str, serial: str):
        self.index = index
        self.model = model
        self.serial = serial
        self.pulse_multiplier = self.get_multiplier(model)

    @staticmethod
    def get_multiplier(model: str):
        if model.startswith("VIVE Controller"):
            return 100.0

        # Vive Tracker, Tundra Tracker, etc
        return 1.0


# This is a definition class for storing user settings per tracker
class TrackerConfig(BaseModel):
    # serial: str
    enabled: bool = True  # Not yet used
    address: str = "" # Deprecated
    address_list: List[str] = []
    multiplier_override: float = 1.0
    pattern_override: str = "None"
    battery_threshold: int = 20
    
    def get_address_str(self):
        if len(self.address_list) == 0:
            self.address_list.append("/avatar/parameters/...")
        
        result = ";".join(self.address_list)
        return result
    
    def set_address(self, value):
        self.address_list = value.split(';')

    def set_vibration_multiplier(self, value):
        if value is None:
            return
        try:
            self.multiplier_override = float(value)
        except ValueError:
            self.multiplier_override = 1.0

    def set_battery_threshold(self, value):
        if value is None:
            return
        try:
            self.battery_threshold = int(value)
        except ValueError:
            self.battery_threshold = 20


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
    version: int = 2
    start_with_steamvr: bool = False
    start_minimized: bool = False
    theme: str = "DarkAmber" # If changing this, also update app_gui.py!
    server_type: int = 0
    server_osc_oscquery: bool = True
    server_ip: str = "127.0.0.1"
    server_port: int = 9001
    pattern_config_list: List[PatternConfig] = []
    tracker_config_dict: Dict[str, TrackerConfig] = {}

    # OBSOLETE - Will delete these in the next version
    tracker_to_osc: Dict[str, str] = {}

    def get_tracker_config(self, device_serial):
        if device_serial in self.tracker_config_dict:
            return self.tracker_config_dict[device_serial]
        result = TrackerConfig()
        self.tracker_config_dict[device_serial] = result
        return result

    def check_integrity(self):
        if len(self.pattern_config_list) != 2:
            self.init_pattern_config()
        for key in self.tracker_to_osc:
            new_config = TrackerConfig()
            new_config.address = self.tracker_to_osc[key]
            self.tracker_config_dict[key] = new_config
        self.tracker_to_osc.clear()
        
        for serial, tracker_config in self.tracker_config_dict.items():
            if tracker_config.address:
                tracker_config.set_address(tracker_config.address)
                tracker_config.address = ''

    def init_pattern_config(self):
        self.pattern_config_list.clear()
        # PROXIMITY Defaults: (Linear, 50, 4)
        from app_pattern import VibrationPattern
        self.pattern_config_list.append(PatternConfig(VibrationPattern.VIB_PATTERN_LIST[4], 0, 80, 4))
        # VELOCITY Defaults: (None, 80, 32)
        self.pattern_config_list.append(PatternConfig(VibrationPattern.VIB_PATTERN_LIST[0], 40, 80, 16))

    @staticmethod
    def load():
        # return AppConfig()
        if os.path.exists(LEGACY_CONFIG_FILE_NAME):
            # Quickly check if config file looks valid without fully loading
            # Guards against enormous unrelated config.json files
            # See https://stackoverflow.com/questions/4940032/how-to-search-for-a-string-in-text-files
            try:
                move_path_needed = False
                with open(LEGACY_CONFIG_FILE_NAME, 'rb', 0) as cfg_file, \
                    mmap.mmap(cfg_file.fileno(), 0, access=mmap.ACCESS_READ) as cfg_txt:
                        if cfg_txt.find(b'tracker_config_dict') != -1:
                            move_path_needed = True
                if move_path_needed:
                    if not os.path.exists(CONFIG_FILE_NAME):
                        print(f"[Config] Moving legacy '{LEGACY_CONFIG_FILE_NAME}' to '{CONFIG_FILE_NAME}'")
                        shutil.move(LEGACY_CONFIG_FILE_NAME, CONFIG_FILE_NAME)
                    else:
                        print(f"[Config] Ignoring legacy '{LEGACY_CONFIG_FILE_NAME}', '{CONFIG_FILE_NAME}' already exists")
                else:
                    print(f"[Config] Contents of legacy '{LEGACY_CONFIG_FILE_NAME}' not recognized, ignoring...")
            except:
                print(f"[Config][ERROR] Couldn't migrate legacy '{LEGACY_CONFIG_FILE_NAME}', ignoring...")

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
            json.dump(self.model_dump(), fp=settings_file, sort_keys=True, indent=4)
