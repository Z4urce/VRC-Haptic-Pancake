import openvr
from config import VRTracker


class OpenVRTracker:
    def __init__(self):
        self.devices: [VRTracker] = []
        self.vr = None

        try:
            self.init_openvr()
        except:
            pass

    def init_openvr(self):
        self.vr = openvr.init(openvr.VRApplication_Background)
        self.devices: [VRTracker] = []

        poses = self.vr.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                        openvr.k_unMaxTrackedDeviceCount)
        for i in range(openvr.k_unMaxTrackedDeviceCount):
            if poses[i].bPoseIsValid and self.vr.getTrackedDeviceClass(i) == openvr.TrackedDeviceClass_GenericTracker:
                self.devices.append(VRTracker(i, self.get_model(i), self.get_serial(i)))

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

    def shutdown(self):
        if self.is_alive():
            self.vr.shutdown()
