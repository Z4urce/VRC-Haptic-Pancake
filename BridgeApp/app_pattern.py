import math
import time

from app_config import AppConfig, PatternConfig


# This class should determine the final vibration intensity for the given tracker
class VibrationPattern:
    PROXIMITY = 0
    VELOCITY = 1

    VIB_PATTERN_LIST = ["None", "Constant", "Linear", "Sine"]

    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.tracker_data = {}
        if len(self.config.pattern_config_list) != 2:
            self.init_pattern_config()

    def init_pattern_config(self):
        self.config.pattern_config_list.clear()
        # PROXIMITY Defaults: (Linear, 50, 4)
        self.config.pattern_config_list.append(PatternConfig(self.VIB_PATTERN_LIST[2], 40, 80, 4))
        # VELOCITY Defaults: (None, 80, 32)
        self.config.pattern_config_list.append(PatternConfig(self.VIB_PATTERN_LIST[0], 40, 80, 32))

    def apply_pattern(self, tracker_serial, osc_value):
        delta_time, delta_value = self.__calculate_delta(tracker_serial, osc_value)
        return self.__apply_pattern(osc_value, delta_value, delta_time)

    def __calculate_delta(self, tracker_serial, osc_value):
        delta_time = 0
        delta_value = 0
        current_time = time.time()
        if tracker_serial in self.tracker_data:
            delta_time = current_time - self.tracker_data[tracker_serial][0]
            delta_value = osc_value - self.tracker_data[tracker_serial][1]
        self.tracker_data[tracker_serial] = (current_time, osc_value)
        return delta_time, delta_value

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
                proximity_value = osc_value
            case 2:  # Linear
                proximity_value = self.__get_linear_value(proximity_settings.speed) * osc_value
            case 3:  # Sine
                proximity_value = self.__get_sine_value(proximity_settings.speed) * osc_value

        match velocity_pattern_index:
            case 0:  # None
                velocity_value = 0
            case 1:  # Constant
                velocity_value = self.__get_velocity_value(osc_value_delta)
            case 2:  # Linear
                velocity_value = self.__get_linear_value(velocity_settings.speed) * self.__get_velocity_value(
                    osc_value_delta)
            case 3:  # Sine
                velocity_value = self.__get_sine_value(velocity_settings.speed) * self.__get_velocity_value(
                    osc_value_delta)

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
    def __get_sine_value(speed):
        # Use the sine function to map the current time to a value between 0 and 1
        result = (math.sin(time.time() * speed) + 1) / 2  # Map from [-1, 1] to [0, 1]
        return max(0, min(result, 1))

    @staticmethod
    def __get_linear_value(speed):
        result = (time.time() * speed) % 2
        return result if (result <= 1) else (2 - result)

    @staticmethod
    def __get_velocity_value(value_delta):
        return abs(value_delta)

    @staticmethod
    def __get_velocity_approaching_value(value_delta):
        return value_delta if value_delta > 0 else 0
