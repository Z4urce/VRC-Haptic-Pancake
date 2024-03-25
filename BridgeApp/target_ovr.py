import openvr
from app_runner import FeedbackThread
from app_config import VRTracker, AppConfig
from typing import List, Dict

## HACK: test spacing out pulses
#import time

class OpenVRTracker:
    def __init__(self, config: AppConfig):
        self.devices: List[VRTracker] = []
        self.vibration_managers: Dict[str, FeedbackThread] = {}
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
                thread = FeedbackThread(self.config, device, self.__pulse, self.get_battery_level)
                thread.daemon = True
                thread.start()
                self.vibration_managers[device.serial] = thread

        return self.devices

    def get_serial(self, index):
        return self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_SerialNumber_String)

    def get_model(self, index):
        try:
            return self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_ModelNumber_String)
        except openvr.error_code.TrackedProp_UnknownProperty:
            # Some devices (e.g. Vive Tracker 1.0) don't report a model number.
            return "Unknown Tracker"

    def get_battery_level(self, index):
        try:
            return self.vr.getFloatTrackedDeviceProperty(index, openvr.Prop_DeviceBatteryPercentage_Float)
        except openvr.error_code.TrackedProp_UnknownProperty:
            # Some devices (e.g. Tundra Trackers) may be delayed in reporting a
            # battery percentage, especially if fully charged.  If missing,
            # assume 100% battery.
            return 1

    def set_strength(self, serial, strength):
        if serial in self.vibration_managers:
            self.vibration_managers[serial].set_strength(strength)

    def pulse_by_serial(self, serial, pulse_length: int = 200):
        if serial in self.vibration_managers:
            self.vibration_managers[serial].force_pulse(pulse_length)

    def is_alive(self):
        return self.vr is not None

    def __pulse(self, index, pulse_length: int = 200):
        if self.is_alive():
            self.vr.triggerHapticPulse(index, 0, pulse_length)
            # HACK: test spacing out pulses
            #pulse_max_amount = 3999
            pulse_max_amount = 5000
            #sleep_min_delay = pulse_max_amount / 1000000
            #sleep_min_delay = 5000 / 1000000
            if pulse_length > pulse_max_amount:
                print("PULSE LENGTH > " + str(pulse_max_amount) + ": " + str(pulse_length))
            #print("PULSE LENGTH: " + str(pulse_length))
            #while pulse_length > 3999:
            #    self.vr.triggerHapticPulse(index, 0, pulse_max_amount)
            #    pulse_length -= pulse_max_amount
            #    time.sleep(sleep_min_delay)
            #if pulse_length > 0:
            #    self.vr.triggerHapticPulse(index, 0, pulse_length)
            #    time.sleep(sleep_min_delay)
