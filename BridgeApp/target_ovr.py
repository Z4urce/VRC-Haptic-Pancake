import openvr
from app_runner import FeedbackThread
from app_config import VRTracker, AppConfig
from typing import List, Dict
from vr_manifest import VRManifest

class OpenVRHandler:
    def __init__(self, config: AppConfig):
        self.devices: List[VRTracker] = []
        self.vibration_managers: Dict[str, FeedbackThread] = {}
        self.vr = None
        self.vr_apps = None
        self.vr_manifest = VRManifest()
        self.config = config

    def try_init_openvr(self, quiet_refresh=False):
        if self.vr is not None:
            return True
        try:
            self.vr = openvr.init(openvr.VRApplication_Background)
            self.vr_apps = openvr.VRApplications()
            self.devices: [VRTracker] = []
            print("[OpenVRHandler] Successfully initialized.")
            return True
        except:
            if not quiet_refresh:
                print("[OpenVRHandler] Failed to initialize OpenVR.")
            return False

    def query_devices(self, quiet_refresh=False):
        if not self.try_init_openvr(quiet_refresh):
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

    @property
    def is_alive(self):
        return self.vr is not None

    @property
    def is_app_bundled(self):
        """Gets if app is bundled in a single file (e.g. PyInstaller)"""
        return self.vr_manifest.is_app_bundled

    @property
    def is_vr_registered(self):
        """Gets if the app is registered with the OpenVR runtime"""
        if not self.is_alive:
            raise RuntimeError("Cannot check if app registered when VR isn't initialized")

        return self.vr_apps.isApplicationInstalled(self.vr_manifest.app_key)

    @property
    def is_vr_autolaunch_enabled(self):
        """Gets if the app is registered with the OpenVR runtime"""
        if not self.is_alive:
            raise RuntimeError("Cannot check if app auto-launching when VR isn't initialized")

        if not self.is_vr_registered:
            return False

        return self.vr_apps.getApplicationAutoLaunch(self.vr_manifest.app_key)

    @property
    def is_manifest_recent(self):
        """Gets if VR manifest file has been saved this launch"""
        return self.vr_manifest.is_recent

    def __pulse(self, index, pulse_length: int = 200):
        if self.is_alive:
            self.vr.triggerHapticPulse(index, 0, pulse_length)

    def resync_autostart(self):
        """Resyncs Haptic Pancake auto-start with VR auto-launch, if possible

        Also refreshes VR manifest file to account for moving the app around
        """
        if not self.try_init_openvr(False):
            return False

        # Check if VR runtime has autostart status changed
        if self.is_vr_registered:
            vr_autolaunch = self.is_vr_autolaunch_enabled
            if self.config.start_with_steamvr != vr_autolaunch:
                print(f"[OpenVRHandler] Auto-launch status changed to {vr_autolaunch == True}, updating config")
                self.config.start_with_steamvr = vr_autolaunch
                self.setup_autostart(vr_autolaunch)
                return True

            # Check if VR manifest hasn't been refreshed (skipped if refreshed above)
            if not self.is_manifest_recent:
                print("[OpenVRHandler] Refreshing manifest as app is already registered")
                self.setup_autostart(self.config.start_with_steamvr)

        return False

    def setup_autostart(self, autostart: bool):
        if not self.try_init_openvr(False):
            return

        if autostart:
            # Always save manifest file so it's kept up-to-date with moving/renaming app
            self.vr_manifest.save()

            if not self.is_vr_registered:
                print(f"[OpenVRHandler] Installing vrmanifest: {self.vr_manifest.manifest_path}")
                self.vr_apps.addApplicationManifest(self.vr_manifest.manifest_path, False)

            if not self.is_vr_autolaunch_enabled:
                print("[OpenVRHandler] Enabling auto launch")
                self.vr_apps.setApplicationAutoLaunch(self.vr_manifest.app_key, True)
        else:
            if self.is_vr_registered:
                # Once installed, ensure manifest file is kept up-to-date with
                # moving/renaming the app, even if autostart is currently disabled.
                self.vr_manifest.save()

                if self.is_vr_autolaunch_enabled:
                    print("[OpenVRHandler] Disabling auto launch")
                    self.vr_apps.setApplicationAutoLaunch(self.vr_manifest.app_key, False)
