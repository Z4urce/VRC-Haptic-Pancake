import threading
import time
from app_pattern import VibrationPattern
from app_config import AppConfig, VRTracker


class FeedbackThread(threading.Thread):
    LOW_BATTERY_ALERT_COUNT = 8

    def __init__(self, config: AppConfig, tracker: VRTracker, pulse_function, battery_function):
        super().__init__()
        self.config = config
        self.tracker = tracker
        self.pulse_function = pulse_function
        self.battery_function = battery_function

        self.tracker_config = config.get_tracker_config(tracker.serial)

        self.battery_low_notif = self.LOW_BATTERY_ALERT_COUNT

        self.strength: float = 0.0  # Should be treated as a value between 0 and 1
        self.strength_delta: float = 0.0
        self.last_str_set_time = time.time()

        self.interval_ms = 50  # millis
        self.interval_s = self.interval_ms / 1000  # seconds

        self.vp = VibrationPattern(self.config)

    def set_strength(self, strength):
        try:
            strength = float(strength)
        except ValueError:
            strength = 0.0

        self.strength_delta += abs(strength - self.strength)
        self.strength = strength
        self.last_str_set_time = time.time()

    def run(self):
        print(f"[VibrationManager] Thread started for {self.tracker.serial}")

        while True:
            start_time = time.time()

            strength = self.calculate_strength(start_time)
            # So we pulse every 50 ms that means a 50 ms pulse would be 100%
            if strength > 0:
                self.pulse_function(self.tracker.index, int(strength * self.interval_ms))

            sleep = max(self.interval_s - (time.time() - start_time), 0.0)
            time.sleep(sleep)

    def calculate_strength(self, start_time):
        # Check the battery threshold
        if self.battery_function(self.tracker.index) < (self.tracker_config.battery_threshold / 100):
            if self.battery_low_notif > 0:
                self.battery_low_notif -= 1
                return self.battery_low_notif % .9
            return 0
        self.battery_low_notif = self.LOW_BATTERY_ALERT_COUNT

        # Apply Pattern
        patterned_strength = self.vp.apply_pattern(self.strength, self.strength_delta)
        self.strength_delta -= patterned_strength
        if self.strength_delta < 0:
            self.strength_delta = 0

        # Apply Multiplier and return
        if patterned_strength > 0:
            return self.apply_multiplier(patterned_strength)

        return 0

    def apply_multiplier(self, strength):
        return (strength * self.tracker.pulse_multiplier
                * self.config.get_tracker_config(self.tracker.serial).multiplier_override)

    def force_pulse(self, length):
        self.pulse_function(self.tracker.index, int(length * self.tracker.pulse_multiplier))
