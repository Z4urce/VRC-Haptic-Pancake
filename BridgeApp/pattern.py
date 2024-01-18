import math
import time

from config import AppConfig


class VibrationPattern:
    VIB_PATTERN_LIST = ["None", "SineSlow", "Sine", "SineFast"]

    def __init__(self, app_config: AppConfig):
        self.config = app_config

    def apply_pattern(self, value):
        pattern = self.config.global_vibration_pattern
        if pattern == self.VIB_PATTERN_LIST[1]:
            return self.get_sine_value(1) * value
        if pattern == self.VIB_PATTERN_LIST[2]:
            return self.get_sine_value(2) * value
        if pattern == self.VIB_PATTERN_LIST[3]:
            return self.get_sine_value(4) * value
        return value

    @staticmethod
    def get_sine_value(speed):
        # Use the sine function to map the current time to a value between 0 and 1
        result = (math.sin(time.time() * speed) + 1) / 2  # Map from [-1, 1] to [0, 1]
        return max(0, min(result, 1))
