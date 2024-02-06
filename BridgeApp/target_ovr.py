import threading
import time
import openvr
from app_config import VRTracker, AppConfig
from typing import List, Dict


class VibrationManager(threading.Thread):
    def __init__(self, tracker: VRTracker, pulse_function, config: AppConfig):
        super().__init__()
        self.tracker = tracker
        self.pulse_function = pulse_function
        self.config = config
        self.strength: float = 0.0  # Should be treated as a value between 0 and 1
        self.last_str_set_time = time.time()

        self.interval_ms = 50  # millis
        self.interval_s = self.interval_ms / 1000  # seconds

    def set_strength(self, strength: float):
        self.strength = strength
        self.last_str_set_time = time.time()

    def run(self):
        print(f"[VibrationManager] Thread started for {self.tracker.serial}")

        while True:
            start_time = time.time()

            # We stop the pulse if we don't get a new value in a certain time
            if self.last_str_set_time + (2*self.interval_s) < start_time:
                self.strength = 0

            # So we pulse every 50 ms that means a 50 ms pulse would be 100%
            if self.strength > 0:
                self.pulse_function(self.tracker.index, int(self.strength * self.interval_ms))

            sleep = max(self.interval_s - (time.time() - start_time), 0.0)
            time.sleep(sleep)


class OpenVRTracker:
    def __init__(self, config: AppConfig):
        self.devices: List[VRTracker] = []
        self.vibration_managers: Dict[str, VibrationManager] = {}
        self.vr = None
        self.config = config

    def try_init_openvr(self):
        if self.vr is not None:
            return True
        try:
            self.vr = openvr.init(openvr.VRApplication_Background)
            self.devices: [VRTracker] = []
            print("[OpenVRTracker] Successfully initialized.")
            return True
        except:
            print("[OpenVRTracker] Failed to initialize OpenVR.")
            return False

    def query_devices(self):
        if not self.try_init_openvr():
            return self.devices

        poses = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                        openvr.k_unMaxTrackedDeviceCount)

        # Add every visible device to the list
        self.devices.clear()
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            if poses[i].bPoseIsValid and self.vr.getTrackedDeviceClass(i) == openvr.TrackedDeviceClass_GenericTracker:
                self.devices.append(VRTracker(i, self.get_model(i), self.get_serial(i)))

        # Start a new thread for each device
        for device in self.devices:
            if device.serial not in self.vibration_managers:
                thread = VibrationManager(device, self.pulse, self.config)
                thread.daemon = True
                thread.start()
                self.vibration_managers[device.serial] = thread

        return self.devices

    def get_serial(self, index):
        return self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_SerialNumber_String)

    def get_model(self, index):
        return self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_ModelNumber_String)

    def set_strength(self, serial, strength):
        if serial in self.vibration_managers:
            self.vibration_managers[serial].strength = strength

    def pulse(self, index, pulse_length: int = 200):
        if self.is_alive():
            self.vr.triggerHapticPulse(index, 0, pulse_length)

    def pulse_by_serial(self, serial, pulse_length: int = 200):
        for device in self.devices:
            if device.serial == serial:
                self.pulse(device.index, pulse_length)
                return

    def is_alive(self):
        return self.vr is not None
