import math
import time

from config import AppConfig


# This class should determine the final vibration intensity for the given tracker
class VibrationPattern:
    VIB_PATTERN_LIST = ["None", "LinearSlow", "Linear", "LinearFast",               # 0, 1, 2, 3
                        "SineSlow", "Sine", "SineFast",                             # 4, 5, 6
                        "Velocity", "VelocityApproaching",                          # 7, 8
                        "VelocityPlusProximity@20%", "VelocityPlusProximity@40%"]   # 9, 10

    def __init__(self, app_config: AppConfig):
        self.config = app_config
        self.tracker_data = {}

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
        pattern = self.config.global_vibration_pattern
        index = self.VIB_PATTERN_LIST.index(pattern)
        value = osc_value * self.config.global_vibration_intensity

        match index:
            case 0:
                return value
            case 1:  # LinearSlow
                return self.__get_linear_value(1) * value
            case 2:  # Linear
                return self.__get_linear_value(2) * value
            case 3:  # LinearFast
                return self.__get_linear_value(4) * value
            case 4:  # SineSlow
                return self.__get_sine_value(8) * value
            case 5:  # Sine
                return self.__get_sine_value(16) * value
            case 6:  # SineFast
                return self.__get_sine_value(32) * value
            case 7:  # Velocity
                return self.__get_velocity_value(osc_value_delta) * value
            case 8:  # VelocityApproaching
                return self.__get_velocity_approaching_value(osc_value_delta) * value
            case 9:  # VelocityPlusProximity@20%
                return max(self.__get_velocity_value(osc_value_delta), .2) * value
            case 10:  # VelocityPlusProximity@40%
                return max(self.__get_velocity_value(osc_value_delta), .4) * value
        return value

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
