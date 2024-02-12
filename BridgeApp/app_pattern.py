import math
import time

from app_config import AppConfig, PatternConfig


# This class should determine the final vibration intensity for the given tracker
class VibrationPattern:
    PROXIMITY = 0
    VELOCITY = 1

    VIB_PATTERN_LIST = ["None", "Constant", "Linear", "Sine", "Throb"]
    VIB_PATTERN_TOOLTIP = ("- None will disable the system.\n"
                           "- Constant will always vibrate at the maximum allowed value\n"
                           "- Linear will vibrate proportionally to the incoming value\n"
                           "- Sine will ease the incoming value\n"
                           "- Throb will pulsate between on and off state to prevent drifting")

    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.tracker_data = {}

    def apply_pattern(self, tracker_serial, osc_value):
        delta_value, delta_time = self.__calculate_delta(tracker_serial, osc_value)
        return self.__apply_pattern(osc_value, delta_value, delta_time)

    def __calculate_delta(self, tracker_serial, osc_value):
        delta_value = 0
        delta_time = 0
        current_time = time.time()
        if tracker_serial in self.tracker_data:
            delta_value = osc_value - self.tracker_data[tracker_serial][0]
            delta_time = current_time - self.tracker_data[tracker_serial][1]
        self.tracker_data[tracker_serial] = (osc_value, current_time)
        return delta_value, delta_time

    def __apply_pattern(self, osc_value, osc_value_delta, delta_time):
        proximity_settings = self.config.pattern_config_list[self.PROXIMITY]
        velocity_settings = self.config.pattern_config_list[self.VELOCITY]
        proximity_pattern_index = self.VIB_PATTERN_LIST.index(proximity_settings.pattern)
        velocity_pattern_index = self.VIB_PATTERN_LIST.index(velocity_settings.pattern)
        proximity_value = velocity_value = 0

        match proximity_pattern_index:
            case 0:  # None
                proximity_value = 0
            case 1:  # Constant
                proximity_value = 1 if osc_value > 0 else 0
            case 2:  # Linear
                proximity_value = osc_value
            case 3:  # Sine
                proximity_value = self.ease_in_out_sine(osc_value)
            case 4:  # Throb
                proximity_value = self.__get_linear_value(proximity_settings.speed) * osc_value

        match velocity_pattern_index:
            case 0:  # None
                velocity_value = 0
            case 1:  # Constant
                velocity_value = 1 if osc_value_delta != 0 else 0
            case 2:  # Linear
                velocity_value = abs(osc_value_delta)
            case 3:  # Sine
                velocity_value = self.ease_in_out_sine(osc_value_delta)
            case 4:  # Throb
                velocity_value = self.__get_linear_value(velocity_settings.speed) * abs(osc_value_delta)

        proximity_value = self.__map(proximity_value, proximity_settings.str_min/100, proximity_settings.str_max/100)
        velocity_value = self.__map(velocity_value, velocity_settings.str_min/100, velocity_settings.str_max/100)

        return max(proximity_value, velocity_value)

    @staticmethod
    def __map(value, right_min, right_max):
        if value == 0:
            return 0

        span = right_max - right_min
        return right_min + (value * span)

    @staticmethod
    def ease_in_out_sine(value: float):
        return -(math.cos(math.pi * value) - 1) / 2.0

    @staticmethod
    def __get_sine_value(speed):
        # Use the sine function to map the current time to a value between 0 and 1
        result: float = (math.sin(time.time() * speed) + 1) / 2.0  # Map from [-1, 1] to [0, 1]
        return max(0.0, min(result, 1.0))

    @staticmethod
    def __get_linear_value(speed):
        result = (time.time() * speed) % 2
        return result if (result <= 1) else (2 - result)
