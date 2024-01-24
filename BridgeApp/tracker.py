import openvr
from config import VRTracker


class OpenVRTracker:
    def __init__(self):
        self.devices: [VRTracker] = []
        self.vr = None

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
        self.devices.clear()
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            if poses[i].bPoseIsValid and self.vr.getTrackedDeviceClass(i) == openvr.TrackedDeviceClass_GenericTracker:
                self.devices.append(VRTracker(i, self.get_model(i), self.get_serial(i)))
        return self.devices

    def get_serial(self, index):
        return self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_SerialNumber_String)

    def get_model(self, index):
        return self.vr.getStringTrackedDeviceProperty(index, openvr.Prop_ModelNumber_String)

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
