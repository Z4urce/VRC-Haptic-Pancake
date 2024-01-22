import math
import time

from config import AppConfig


class VibrationPattern:
    VIB_PATTERN_LIST = ["None", "LinearSlow", "Linear", "LinearFast", "SineSlow", "Sine", "SineFast"]

    def __init__(self, app_config: AppConfig):
        self.config = app_config

    def apply_pattern(self, value):
        pattern = self.config.global_vibration_pattern
        index = self.VIB_PATTERN_LIST.index(pattern)

        match index:
            case 0:
                return value
            case 1:  # LinearSlow
                return self.get_linear_value(8) * value
            case 2:  # Linear
                return self.get_linear_value(16) * value
            case 3:  # LinearFast
                return self.get_linear_value(32) * value
            case 4:  # SineSlow
                return self.get_sine_value(8) * value
            case 5:  # Sine
                return self.get_sine_value(16) * value
            case 6:  # SineFast
                return self.get_sine_value(32) * value
        return value

    @staticmethod
    def get_sine_value(speed):
        # Use the sine function to map the current time to a value between 0 and 1
        result = (math.sin(time.time() * speed) + 1) / 2  # Map from [-1, 1] to [0, 1]
        return max(0, min(result, 1))

    @staticmethod
    def get_linear_value(speed):
        result = (time.time() * speed) % 2
        return result if (result <= 1) else (2 - result)

    @staticmethod
    def linear_interpolation(value1, value2, fraction):
        return value1 + (value2 - value1) * fraction
