import openvr
from app_runner import FeedbackThread
from app_config import VRTracker, AppConfig
from typing import List, Dict


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
            result = self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_ModelNumber_String)
        except openvr.error_code.TrackedProp_UnknownProperty:
            result = "Unknown Tracker"
        return result

    def get_battery_level(self, index):
        return self.vr.getFloatTrackedDeviceProperty(index, openvr.Prop_DeviceBatteryPercentage_Float)

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
