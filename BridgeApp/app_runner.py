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
        # If true, the warning for strength exceeding 1.0 (100%) has been shown
        # Resets on changing strength
        self.shown_strength_exceed_max = False

        # Some devices (e.g. Tundra Trackers) use microseconds instead of
        # milliseconds for the legacy triggerHapticPulse() function, but then
        # limit you to around 3999µs per pulse.
        #
        # TODO: That number is probably not exact; check with an oscilloscope.
        #
        # See https://steamcommunity.com/app/358720/discussions/0/405693392914144440/
        #
        # In these situations, the update loop needs to run much faster to
        # avoid exceeding the maximum duration of one haptic pulse.  Any manual
        # pulses also need to be spread out over time to not exceed the limit.
        #
        # TODO: Try switching from "triggerHapticPulse()" to IVRInput
        # triggerHapticPulse() is deprecated as per Valve:
        # * https://github.com/ValveSoftware/openvr/blob/v2.2.3/headers/openvr.h#L2431-L2433
        # * https://github.com/ValveSoftware/openvr/blob/v2.2.3/headers/openvr.h#L5216-L5218
        #
        # This might be specific to Tundra Trackers vs. Vive Trackers, as
        # Tundra ships their IO Expansion board with a LRA/haptic actuator

        # Assume trackers that behave as expected
        self.interval_ms = 50  # millis

        # Hack: multiplier to convert from milliseconds to the actual unit
        self.hack_pulse_mult_to_ms = 0
        # Hack: maximum allowed pulse duration in milliseconds
        self.hack_pulse_limit_ms = 0
        # Hack: when to stop a queued force pulse
        self.hack_pulse_force_stop_time = 0

        # Special-case as needed
        if self.tracker.model.startswith("Tundra"):
            # Tundra Tracker
            # Works in microseconds
            self.hack_pulse_mult_to_ms = 1 / 1000
            # Has a limit of roughly 4000 microseconds
            self.hack_pulse_limit_ms = 4000 * self.hack_pulse_mult_to_ms

        if self.hack_pulse_limit_ms > 0:
            # Apply pulse duration hack/workaround
            self.interval_ms = self.hack_pulse_limit_ms
            print(f"[VibrationManager] Using {self.interval_ms} ms pulse limit workaround for {self.tracker.serial}")

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
        self.shown_strength_exceed_max = False

    def run(self):
        print(f"[VibrationManager] Thread started for {self.tracker.serial}")

        while True:
            start_time = time.time()

            pulse_length = 0

            strength = self.calculate_strength(start_time)
            if strength > 0:
                # Warn if strength exceeds 100%
                if strength > 1 and not self.shown_strength_exceed_max:
                    print(f"[VibrationManager] Strength >100% ({round(strength * 100)}) for {self.tracker.serial}, multiplier too high?")
                    self.shown_strength_exceed_max = True
                    # Don't cap strength to 1.0 as some may rely on overriding
                    # the multiplier to adjust for different timescales, etc.

                # So we pulse every self.interval_ms (e.g. 50) ms.  That means a
                # self.interval_ms (50/etc) ms pulse would be 100%.
                pulse_length = strength * self.interval_ms

            # Check if there's a queued force pulse
            if start_time < self.hack_pulse_force_stop_time:
                # Convert to milliseconds
                force_pulse_duration = (self.hack_pulse_force_stop_time - start_time) * 1000
                # Pick the biggest number for pulse_length
                pulse_length = max(pulse_length, force_pulse_duration)

            # If a maximum pulse length is specified, cap the result.
            # Exceeding the limit can result in sporadic vibration instead of
            # a max strength (continuous) pulse.
            if self.hack_pulse_limit_ms > 0:
                pulse_length = min(pulse_length, self.hack_pulse_limit_ms)

            # Convert to target unit of time if necessary
            if self.hack_pulse_mult_to_ms:
                pulse_length = pulse_length / self.hack_pulse_mult_to_ms

            # Convert to integer (after all else for max precision)
            pulse_length = int(pulse_length)

            # Trigger pulse if nonzero length requested
            if pulse_length > 0:
                self.pulse_function(self.tracker.index, pulse_length)

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
        if self.hack_pulse_limit_ms > 0:
            # Add the pulse length in milliseconds to the current time in
            # seconds, determining the new target time to stop
            self.hack_pulse_force_stop_time = time.time() + (length / 1000)
        else:
            # Convert to target unit of time if necessary
            if self.hack_pulse_mult_to_ms:
                length = length / self.hack_pulse_mult_to_ms
            # Trigger haptic pulse
            self.pulse_function(self.tracker.index, int(length * self.tracker.pulse_multiplier))
