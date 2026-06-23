import FreeSimpleGUI as sg
import webbrowser

from app_config import AppConfig, PatternConfig
from app_pattern import VibrationPattern

import platform_conf

WINDOW_NAME = "Haptic Pancake Bridge v0.8.0-beta.4"
WINDOW_NAME_UNBUNDLED = WINDOW_NAME + " (unbundled)"
WINDOW_ICON = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpVIrDhYVcchQnezgB+JYqlgEC6Wt0KqDyaVf0KQhSXFxFFwLDn4sVh1cnHV1cBUEwQ8QZwcnRRcp8X9NoUWMB8f9eHfvcfcOEOplpppdEUDVLCMZi4qZ7Kroe0UvBjEEPyYlZurx1GIaruPrHh6+3oV5lvu5P0efkjMZ4BGJI0w3LOIN4tlNS+e8TxxkRUkhPieeMOiCxI9clx1+41xossAzg0Y6OU8cJBYLHSx3MCsaKvEMcUhRNcoXMg4rnLc4q+Uqa92TvzCQ01ZSXKc5ihiWEEcCImRUUUIZFsK0aqSYSNJ+1MU/0vQnyCWTqwRGjgVUoEJq+sH/4He3Zn56ykkKRIHuF9v+GAN8u0CjZtvfx7bdOAG8z8CV1vZX6sDcJ+m1thY6Avq3gYvrtibvAZc7wPCTLhlSU/LSFPJ54P2MvikLDNwC/jWnt9Y+Th+ANHW1fAMcHALjBcped3l3T2dv/55p9fcD3S9y0apk9h0AAAAGYktHRAD/AP8A/6C9p5MAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfoCxYXCzDoJVaPAAACuElEQVQ4y2WTTW8bdRDGfzO767f1xnGcJiSNVNoKqMoJgRBCwifuIHFFuSDRTwDi2CNfgC/gGxfElV6ockEISAJBiAJ5KVnqxk7idbx+ie39DwcngaqH0Wj0HJ756ZmRjz7940Ym0nCe1DMVnArZRbn/d+85bcMJ6744GqrUzYFimIAamMF5P8GCAC1GqAMDlFk3qItKQ9WsrmaoGd32LjYeMeg0edj4mOP9Hzj4/ku2v77PJO3MtPZj1GYmYlb31c1ch2ct5uZW6XZikpN9Rr02v377BenRNsuvvkfa2sUP5wlKFbJhDy1FmAm+GpiD6XkfRFGDfD7infc/p9XcobTwGbmoRpq2sKBI8VqNXjemUCijAr6YXa2kCL74RHOrEORYufkW5vk4haJlOAQFyDLUAAeqzhBn5IOQwMsxGfUo5MqMBwm++IjLmPQTovk1PFFGyVPCygpqhphdIBiUS4t0zg5ZWrqL84RcWL2KraTgVPEWb5KmLQIvT+bsWYThIKF1+BO9XpPDg+9YufU2raPfqCy/zOnJHvlyFcmVyMhYq65h/yGAOGA64cmjBxzHW/Tbf5Ec/c5Z6xFh+RphtESvfUAn3mFh+Q5yEbuYoZc3oAbVxZc4T2KiuRcYnP7N3dc/JCzVZjpGLiiyv/kVl6bqDPnk3o51ksc0n25SrFwn85TxdIRXiBi7Mc5Tpm5CYX6F5uGP5Mo1BoMON974AK8YzRCycUpn9yHd5i9M0xO6/2xzGm9ynsSEpRrZ8Ixee4+9b+5TrqzSP96buV8ieA5eefMeMh7Re/IzleqLyGSEOkcn3iKJt+i3/qR2612GpzGlcBFPfdSBL8bG/MLtulMhfO06mQoWBLMIRXCesnZn+sxnLtkUTzww2/AxWw+8fMOJ1NUv4Lzn39lXIVOu5kAFJ7rhnK3/C07bcJ2GHOyzAAAAAElFTkSuQmCC'

# If changing order, also change update_oscquery_state()
LIST_SERVER_TYPE = ["OSC (VRChat)", "WebSocket (Resonite)"]
LIST_THEME = [] # Initialized in __init__

KEY_PRESET_HEAD = "-BTN-PRESET-HEAD-"
KEY_PRESET_ELBOW_LEFT = "-BTN-PRESET-ELBOW-LEFT-"
KEY_PRESET_ELBOW_RIGHT = "-BTN-PRESET-ELBOW-RIGHT-"
KEY_PRESET_CHEST = "-BTN-PRESET-CHEST-"
KEY_PRESET_HIPS_CHEST = "-BTN-PRESET-HIPS-CHEST-"
KEY_PRESET_HIPS = "-BTN-PRESET-HIPS-"
KEY_PRESET_KNEE_LEFT = "-BTN-PRESET-KNEE-LEFT-"
KEY_PRESET_KNEE_RIGHT = "-BTN-PRESET-KNEE-RIGHT-"
KEY_PRESET_FOOT_LEFT = "-BTN-PRESET-FOOT-LEFT-"
KEY_PRESET_FOOT_RIGHT = "-BTN-PRESET-FOOT-RIGHT-"
# TODO: What names make sense for Resonite?  Could adapt based on server type
PRESET_ADDRESSES = {
    KEY_PRESET_HEAD:
        "/avatar/parameters/HapticHead",
    KEY_PRESET_ELBOW_LEFT:
        "/avatar/parameters/HapticElbowLeft",
    KEY_PRESET_ELBOW_RIGHT:
        "/avatar/parameters/HapticElbowRight",
    KEY_PRESET_CHEST:
        "/avatar/parameters/HapticChest",
    KEY_PRESET_HIPS_CHEST:
        "/avatar/parameters/HapticHips;/avatar/parameters/HapticChest",
    KEY_PRESET_HIPS:
        "/avatar/parameters/HapticHips",
    KEY_PRESET_KNEE_LEFT:
        "/avatar/parameters/HapticKneeLeft",
    KEY_PRESET_KNEE_RIGHT:
        "/avatar/parameters/HapticKneeRight",
    KEY_PRESET_FOOT_LEFT:
        "/avatar/parameters/HapticFootLeft",
    KEY_PRESET_FOOT_RIGHT:
        "/avatar/parameters/HapticFootRight",
    }

KEY_SERVER_TYPE = '-SERVER-TYPE-'
KEY_SERVER_OSCQUERY = '-SERVER-OSCQUERY-'
KEY_REC_IP = '-REC-IP-'
KEY_REC_PORT = '-REC-PORT-'
KEY_BTN_APPLY = '-BTN-APPLY-'
KEY_BTN_REFRESH = '-BTN-REFRESH'
KEY_OPEN_URL_HOME= '-OPENURL'
KEY_OPEN_URL_DONATE = '-OPENDONATE'
KEY_OSC_STATUS_BAR = '-OSC-STATUS-BAR-'
KEY_TRACKER_STATUS_BAR = '-TRACKER-STATUS-BAR-'
KEY_LAYOUT_TRACKERS = '-LAYOUT-TRACKERS-'
KEY_OSC_ADDRESS = '-ADDRESS-OF-'
KEY_VIB_STR_OVERRIDE = '-VIB-STR-'
KEY_BTN_SETUP = '-BTN-SETUP-'
KEY_BTN_TEST = '-BTN-TEST-'
KEY_BTN_CALIBRATE = '-BTN-CALIBRATE-'
KEY_BTN_ADD_EXTERNAL = '-BTN-ADD-EXTERNAL-'
KEY_BTN_DEBUG = '-BTN-DEBUG-'
KEY_BATTERY_THRESHOLD = '-BATTERY-'
KEY_START_WITH_STEAMVR = '-START-WITH-STEAMVR-'
KEY_AUTOSTART_STATUS_BAR = '-AUTOSTART-STATUS-BAR-'
KEY_START_MINIMIZED = '-START-MINIMIZED-'
KEY_THEME = '-THEME-'
KEY_BTN_THEME_RESET = '-BTN-THEME-RESET-'
KEY_NO_DATA_ENABLED = '-NO-DATA-ENABLED-'
KEY_NO_DATA_TIMEOUT = '-NO-DATA-TIMEOUT-'

# Pattern Config
KEY_PROXIMITY = '-PROXY-'
KEY_VELOCITY = '-VELOCITY-'
# Pattern Settings
KEY_VIB_STR_MIN = '-VIB-STR-MIN-'
KEY_VIB_STR_MAX = '-VIB-STR-MAX-'
KEY_VIB_PATTERN = '-VIB-PTN-'
KEY_VIB_SPEED = '-VIB-SPD-'

# Background refresh
KEY_TIMER_REFRESH = '-TIMER-REFRESH-'
TIMER_REFRESH_MS = 10 * 1000

# Resaving config
KEY_SAVE_TO_CONFIG = '-FAUX-SAVE-EVENT-'

# Debug window
KEY_DEBUG_BTN_CLEAR = '-DEBUG-BTN-CLEAR-'
KEY_DEBUG_BTN_COPY = '-DEBUG-BTN-COPY-'
KEY_DEBUG_BTN_REFRESH = '-DEBUG-BTN-REFRESH-'
KEY_DEBUG_CHK_AUTOREFRESH = '-DEBUG-CHK-AUTOREFRESH-'
KEY_DEBUG_INPUT_FILTER = '-DEBUG-INPUT-FILTER-'
KEY_DEBUG_TBL_ADDRESS= '-DEBUG-TBL-ADDRESS-'
KEY_DEBUG_TIMER_REFRESH = '-DEBUG-TIMER-REFRESH-'
DEBUG_TIMER_REFRESH_MS = 0.5 * 1000

# If changing this, also update app_config.py!
DEFAULT_THEME="DarkAmber"

class GUIRenderer:
    def __init__(self, app_config: AppConfig, tracker_test_event,
                 restart_osc_event, refresh_vr_event, add_external_event, setup_autostart_event):
        self.tracker_test_event = tracker_test_event
        self.restart_osc_event = restart_osc_event
        self.refresh_vr_event = refresh_vr_event
        self.add_external_event = add_external_event
        self.setup_autostart_event = setup_autostart_event

        # HACK: Py/FreeSimpleGUI has a fun bug where if the main thread gets
        # blocked for some time when changing properties (e.g. TextColor), the
        # new property value will be shown but not stored in the widget.
        # Instead of dealing with that, just cache the OSC status text/color
        # here for whenever the UI needs recreated.
        self.cache_osc_status_bar_text = 'Loading...'
        self.cache_osc_status_bar_color = None
        self.cache_server_apply_disabled = True
        # HACK: Another fun bug - sometimes the initialization order means that
        # the status text simply doesn't get set!  Do a one-time force refresh
        # to work around this.
        self.cache_force_refresh = True

        self.config = app_config
        self.shutting_down = False
        self.window = None
        self.debug_popup = None
        self.layout_dirty = False
        self.trackers = []

        # Add custom themes
        sg.theme_add_new('OLEDPurple', {'BACKGROUND': '#000000','TEXT': '#FFFFFF','INPUT': '#4D4D4D','TEXT_INPUT': '#FFFFFF','SCROLL': '#707070','BUTTON': ('#FFFFFF', '#371f76'),'PROGRESS': ('#000000','#000000'),'BORDER': 1,'SLIDER_DEPTH': 0,'PROGRESS_DEPTH': 0,})
        global LIST_THEME
        LIST_THEME = sg.theme_list()

        # Load theme from config
        #
        # NOTE: You can't just try/catch! PySimpleGui helpfully prevents errors
        # from happening, printing this to console...
        #
        # > ** Warning - InvalidTheme Theme is not a valid theme. Change your theme call. **
        # > valid values are ['Black', 'Black2', [...] 'Topanga']
        # > Instead, please enjoy a random Theme named DarkBrown4
        #
        # Yes, it could randomly pick HotDogStand :I

        if self.config.theme in LIST_THEME:
            sg.theme(self.config.theme)
        else:
            print(f"[GUI] Couldn't find requested theme '{self.config.theme}', defaulting to {DEFAULT_THEME}")
            sg.theme(DEFAULT_THEME)
            self.config.theme = DEFAULT_THEME

        self.build_layout()

    def build_layout(self):
        # Ideally these would be updated to maintain contrast
        self.theme_color_bad = "red"
        self.theme_color_good = "lime"
        # Help with alignment
        small_button_size = 6

        self.layout = []

        self.autostart_chkbox = sg.Checkbox("Start with SteamVR", default=self.config.start_with_steamvr, key=KEY_START_WITH_STEAMVR, enable_events=True, tooltip="Open Haptic Pancake Bridge when opening SteamVR.")
        self.autostart_status_bar = sg.Text('', key=KEY_AUTOSTART_STATUS_BAR)
        self.osc_status_bar = sg.Text(self.cache_osc_status_bar_text, key=KEY_OSC_STATUS_BAR, text_color=self.cache_osc_status_bar_color)
        self.tracker_status_bar = sg.Text('', key=KEY_TRACKER_STATUS_BAR, font='_ 14')
        self.tracker_frame = sg.Column([], key=KEY_LAYOUT_TRACKERS, scrollable=True, vertical_scroll_only=True, expand_y=True, expand_x = True, size=(400,120))

        proximity_frame = sg.Frame('Proximity Feedback', tooltip="Closer object means stronger vibration.",
                                   layout=self.build_pattern_setting_layout(
                                       KEY_PROXIMITY, VibrationPattern.VIB_PATTERN_LIST,
                                       self.config.pattern_config_list[VibrationPattern.PROXIMITY]))
        velocity_frame = sg.Frame('Velocity Feedback', tooltip="Faster object means stronger vibration",
                                  layout=self.build_pattern_setting_layout(
                                      KEY_VELOCITY, VibrationPattern.VIB_PATTERN_LIST,
                                      self.config.pattern_config_list[VibrationPattern.VELOCITY]))

        external_devices = ['Add', ['Emulated (Sound)::EMUSND', 'Emulated (Text)::EMUTXT',
                                    'Serial (COM port)::SERIALCOM', 'Network (Server)::NETWORK']]
        add_external_button = sg.ButtonMenu("Add External device", external_devices, key=KEY_BTN_ADD_EXTERNAL, disabled=True,
                                            tooltip="Add an external feedback device")

        self.server_oscquery_chkbox = sg.Checkbox("Auto-detect port (OSCQuery)",
            default=self.config.server_osc_oscquery, key=KEY_SERVER_OSCQUERY, enable_events=True,
            tooltip="Use OSCQuery to automatically pick an OSC port for VRChat", pad=0)
        # Py/FreeSimpleGUI's "disabled" state for InputText is hard to read on most themes
        # Replace with a simple Text string instead
        self.server_port_input = sg.InputText(self.config.server_port, key=KEY_REC_PORT, size=13)
        self.server_port_auto = sg.Text("[automatic]", size=13, visible=False)
        self.server_apply_btn = sg.Button("Apply", key=KEY_BTN_APPLY, size=small_button_size, tooltip="Apply and restart server.", disabled=self.cache_server_apply_disabled)

        self.no_data_timeout = sg.Spin(
            [num for num in range(1, 601)], self.config.no_data_timeout, size=4, pad=((0,3),(0,0)),
            key=KEY_NO_DATA_TIMEOUT, enable_events=True, disabled=not self.config.no_data_enabled)

        self.layout = [
            [sg.Text('App settings:', font='_ 14')],
            [self.autostart_chkbox, sg.Push(), self.autostart_status_bar],
            [sg.Checkbox("Start minimized", default=self.config.start_minimized, key=KEY_START_MINIMIZED, enable_events=True)],
            [sg.Text("Theme:", justification='right', size=7),
             sg.InputCombo(LIST_THEME, self.config.theme, key=KEY_THEME, readonly=True, enable_events=True, tooltip="Change app theme.\nCAUTION: Some themes are hard to read.  Be ready to reset."),
             sg.Button("Reset", key=KEY_BTN_THEME_RESET, size=small_button_size, tooltip=f"Reset theme to default ({DEFAULT_THEME})")],
            [sg.Text('Server settings:', font='_ 14'),
             sg.Push(),
             sg.Button("Debug", key=KEY_BTN_DEBUG, size=small_button_size)],
            [sg.Text("Type:", justification='right', size=7),
             sg.InputCombo(LIST_SERVER_TYPE, LIST_SERVER_TYPE[self.config.server_type], key=KEY_SERVER_TYPE, readonly=True, enable_events=True),
             sg.pin(self.server_oscquery_chkbox)],
            [sg.Text("Address:", justification='right', size=7),
             sg.InputText(self.config.server_ip, k=KEY_REC_IP, size=23, tooltip="IP Address. Default is 127.0.0.1"),
             sg.Text("Port:", tooltip="UDP Port. Default is 9001"),
             sg.pin(self.server_port_input),
             sg.pin(self.server_port_auto),
             sg.Push(),
             self.server_apply_btn],
            [sg.Text("Status:", justification='right', size=7), self.osc_status_bar],
            [sg.Text('Haptic settings:', font='_ 14')],
            [sg.Push(), proximity_frame, velocity_frame, sg.Push()],
            [sg.Checkbox("Stop stuck haptics after", default=self.config.no_data_enabled, key=KEY_NO_DATA_ENABLED, enable_events=True),
             self.no_data_timeout,
             sg.Text("(seconds)")],
            # Padding from "Stop stuck haptics" checkbox removes the need for this:
            #[self.small_vertical_space()],
            [sg.Text('Devices:', font='_ 14'),
             self.tracker_status_bar,
             sg.Push(),
             sg.Button("Refresh", key=KEY_BTN_REFRESH, size=small_button_size)],
            # add_external_button],
            [self.tracker_frame],
            [sg.HSep()],
            [sg.Text("Made by BIT FOX DEN / Zelus", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL_HOME), sg.Push(),
             sg.Text("Enjoy Haptic Pancake?  Consider donating", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL_DONATE),
             sg.Sizegrip()],
        ]

        # HACK: Force a refresh of the OSC status bar after reloading, just in
        # case the wrong details get shown.
        self.cache_force_refresh = True

    @staticmethod
    def build_pattern_setting_layout(key: str, pattern_list: [str], pattern_config: PatternConfig):
        speed_tooltip = "Defines the speed of the Throb pattern"
        pattern_tooltip = VibrationPattern.VIB_PATTERN_TOOLTIP

        return [
            [sg.Text("Pattern:", justification='right', size=8, tooltip=pattern_tooltip),
             sg.Drop(pattern_list, pattern_config.pattern, tooltip=pattern_tooltip,
                     k=key + KEY_VIB_PATTERN, size=17, readonly=True, enable_events=True)],
            [sg.Text("Strength:", justification='right', size=8),
             sg.Text("Min:", pad=((3,0),(0,0))),
             sg.Spin([num for num in range(0, 101)], pattern_config.str_min, size=3, pad=((0,3),(0,0)),
                     key=key + KEY_VIB_STR_MIN, enable_events=True),
             sg.Text("Max:", pad=0),
             sg.Spin([num for num in range(0, 101)], pattern_config.str_max, size=3, pad=((0,3),(0,0)),
                     key=key + KEY_VIB_STR_MAX, enable_events=True)],
            [sg.Text("Speed:", justification='right', size=8, tooltip=speed_tooltip),
             sg.Slider(range=(1, 32), size=(15, 10), default_value=pattern_config.speed, tooltip=speed_tooltip,
                       orientation='horizontal', key=key + KEY_VIB_SPEED, enable_events=True)],
        ]

    @staticmethod
    def small_vertical_space():
        return sg.Text('', font=('AnyFont', 1), auto_size_text=True)

    def device_row(self, tracker_serial, tracker_model, additional_layout, icon=None, color=None, quiet_refresh=False):
        if icon is None:
            icon = "⚫"

        string = f"{tracker_serial} {tracker_model}"

        dev_config = self.config.get_tracker_config(tracker_serial)
        address = dev_config.get_address_str()
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold

        multiplier_tooltip = "Additional strength multiplier\nCompensates for different trackers\n1.0 for default (Vive/Tundra Tracker)\n200 for Vive Wand\n400 for Index c."

        if not quiet_refresh:
            print(f"[GUI] Adding tracker: {string}")
        layout = [
            [sg.Checkbox('', default=True, disabled=True, pad=0), sg.Text(icon, text_color=color, pad=0), sg.Text(string, pad=(0, 0))],
            [sg.Text(" "), sg.Text("Address:"),
             sg.InputText(address, k=(KEY_OSC_ADDRESS, tracker_serial),
                          enable_events=True, size=30, pad=((0,5), (0,0)),
                          tooltip="OSC Address or Resonite Address"),
             sg.Button("Setup", k=(KEY_BTN_SETUP, tracker_serial),
                           tooltip="Set tracker address to a standard preset (e.g. Left Foot)", pad=1, size=5),
             sg.Button("Identify", k=(KEY_BTN_TEST, tracker_serial),
                       tooltip="Send a 500ms pulse to the tracker", size=5)],
            additional_layout]

        row = [sg.pin(sg.Col(layout, key=('-ROW-', tracker_serial)))]
        return row

    def tracker_row(self, tracker_serial, tracker_model, color=None, quiet_refresh=False):
        dev_config = self.config.get_tracker_config(tracker_serial)
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold
        multiplier_tooltip = "The haptic intensity for this tracker will be multiplied by this number"

        tr = [sg.Text(" "),
              sg.Text("Battery threshold:", tooltip="Disables vibration bellow this battery level"),
              sg.Spin([num for num in range(0, 90)], battery_threshold, size=3, pad=0,
                      key=(KEY_BATTERY_THRESHOLD, tracker_serial), enable_events=True),
              sg.Text("%", pad=0),
              sg.VSeparator(),
              sg.Text("Pulse multiplier:", tooltip=multiplier_tooltip, pad=0),
              sg.InputText(vib_multiplier, k=(KEY_VIB_STR_OVERRIDE, tracker_serial), enable_events=True,
                           size=4, tooltip=multiplier_tooltip),
              ]
              #sg.Button("Calibrate", button_color='grey', disabled=True, key=(KEY_BTN_CALIBRATE, tracker_serial),
              #          tooltip="Coming soon...")]
        return self.device_row(tracker_serial, tracker_model, tr, color=color, quiet_refresh=quiet_refresh)

    def add_tracker(self, tracker_serial, tracker_model, is_online=False, quiet_refresh=False):
        row = [self.tracker_row(tracker_serial, tracker_model, color=self.theme_color_good if is_online else self.theme_color_bad, quiet_refresh=quiet_refresh)]
        self.add_target(tracker_serial, tracker_model, row, quiet_refresh)

    def add_external_device(self, device_serial, device_model):
        layout = []
        icon = None

        if device_serial.startswith("EMUSND"):
            layout.append(sg.Text(" "))
            layout.append(sg.Text("Sound:", size=6))
            layout.append(sg.InputText("Default", size=35))
            layout.append(sg.FileBrowse("Browse", key=(KEY_BTN_TEST, device_serial)))
            icon = "🔊"
        if device_serial.startswith("EMUTXT"):
            layout.append(sg.Text(" "))
            layout.append(sg.Button("Open Output Window"))
            icon = "📝"
        if device_serial.startswith("SERIALCOM"):
            layout.append(sg.Text(" "))
            layout.append(sg.Text("COM Port:", size=8))
            layout.append(sg.InputText("COM6", size=33))
            layout.append(sg.FileBrowse("Browse", key=(KEY_BTN_TEST, device_serial)))
            icon = "〰"
        if device_serial.startswith("NETWORK"):
            layout.append(sg.Text(" "))
            layout.append(sg.Text("Server IP:", size=8))
            layout.append(sg.InputText("192.168.1.67", size=33))
            icon = "📡"

        row = [self.device_row(device_serial, device_model, layout, icon=icon)]
        self.add_target(device_serial, device_model, row)

    def add_target(self, tracker_serial, tracker_model, layout, quiet_refresh):
        if tracker_serial in self.trackers:
            if not quiet_refresh:
                print(f"[GUI] Tracker {tracker_serial} is already on the list. Skipping...")
            return

        # row = [self.tracker_row(tracker_serial, tracker_model)]
        if self.window is not None:
            self.window.extend_layout(self.tracker_frame, layout)
            self.refresh()
        else:
            self.tracker_frame.layout(layout)

        self.trackers.append(tracker_serial)

    def add_message(self, message):
        self.layout.append([sg.HSep()])
        self.layout.append([sg.Text(message, text_color=self.theme_color_bad)])

    def update_osc_status_bar(self, message, is_error=False, is_busy=False):
        text_color = self.theme_color_bad if is_error else self.theme_color_good
        # Update cache
        self.cache_osc_status_bar_text = message
        self.cache_osc_status_bar_color = text_color
        self.cache_server_apply_disabled = is_busy
        if self.window is None:
            self.osc_status_bar.DisplayText = message
            self.osc_status_bar.TextColor = text_color
            self.server_apply_btn.Disabled = is_busy
            return
        if not self.shutting_down:
            try:
                self.osc_status_bar.update(message, text_color=text_color)
                self.server_apply_btn.update(disabled=is_busy)
            except Exception as e:
                print("[GUI] Failed to update server status bar.")

    def update_tracker_counts(self):
        # Update device count
        #message = "{0} / {1}".format(online, total)
        message = str(len(self.trackers))

        if self.window is None:
            self.tracker_status_bar.DisplayText = message
            return
        if not self.shutting_down:
            try:
                self.tracker_status_bar.update(message)
            except Exception as e:
                print("[GUI] Failed to update tracker status bar.")

    def update_autostart_active(self, autolaunch_enabled):
        if self.window is None:
            self.autostart_chkbox.Value = autolaunch_enabled
            return
        if not self.shutting_down:
            try:
                self.autostart_chkbox.update(autolaunch_enabled)
            except Exception as e:
                print("[GUI] Failed to update autostart checkbox.")

    def update_autostart_status(self, vr_ready):
        if not vr_ready:
            unavailable = True
            message = "SteamVR closed (open to apply changes)"
        else:
            unavailable = False
            message = "SteamVR running"

        text_color = self.theme_color_bad if unavailable else self.theme_color_good

        if self.window is None:
            self.autostart_status_bar.DisplayText = message
            self.autostart_status_bar.TextColor = text_color
            return
        if not self.shutting_down:
            try:
                self.autostart_status_bar.update(message, text_color=text_color)
            except Exception as e:
                print("[GUI] Failed to update autostart status bar.")

    def update_oscquery_state(self):
        oscquery_available = False

        if self.config.server_type == 0:
            # First item is OSC (VRChat)
            oscquery_available = True

        oscquery_active = False
        # Only count as active if also available
        if oscquery_available:
            oscquery_active = self.config.server_osc_oscquery

        if self.window is None:
            self.server_oscquery_chkbox.Visible = oscquery_available
            self.server_port_input.Visible = not oscquery_active
            self.server_port_auto.Visible = oscquery_active
            return
        if not self.shutting_down:
            try:
                self.server_oscquery_chkbox.update(visible=oscquery_available)
                self.server_port_input.update(visible=not oscquery_active)
                self.server_port_auto.update(visible=oscquery_active)
            except Exception as e:
                print("[GUI] Failed to update OSCQuery UI state.")

    def update_no_data_status(self, is_enabled):
        if self.window is None:
            self.no_data_timeout.Disabled = not is_enabled
            return
        if not self.shutting_down:
            try:
                self.no_data_timeout.update(disabled=not is_enabled)
            except Exception as e:
                print(e)
                print("[GUI] Failed to update no data timeout input.")

    def refresh(self):
        self.tracker_frame.contents_changed()
        self.tracker_frame.set_vscroll_position(1)
        self.window.refresh()
        self.layout_dirty = False


    def create_window(self):
        final_window_title = WINDOW_NAME
        if not platform_conf.GET_IS_APP_BUNDLED():
            final_window_title = WINDOW_NAME_UNBUNDLED

        self.window = sg.Window(final_window_title, self.layout, keep_on_top=False, finalize=True, alpha_channel=1, icon=WINDOW_ICON)

        self.window.set_resizable(False, True)

        # Lock in current window size as minimum
        self.window.set_min_size(self.window.size)
        # Expand from minimum size in Y direction
        self.window.size = (self.window.size[0], self.window.size[1] + 150)

        # Start background refresh timer
        self.window.timer_start(TIMER_REFRESH_MS, key=KEY_TIMER_REFRESH, repeating=False)

        # Sync up with config state
        self.update_oscquery_state()

        # Set hand cursor
        self.window[KEY_OPEN_URL_DONATE].set_cursor("hand1")
        self.window[KEY_OPEN_URL_HOME].set_cursor("hand1")


    def recreate_window(self):
        # Close window, recreate new layout and recreate window
        self.shutting_down = True
        self.window.close()
        self.window = None
        self.shutting_down = False
        self.build_layout()
        self.create_window()

        # Refresh trackers/etc because it's too much of a pain to cache them and re-add them
        self.trackers = []
        self.refresh_vr_event()

        # Mark layout as dirty
        self.layout_dirty = True


    def run(self):
        if self.window is None:
            self.create_window()

            # Only minimize window on start, not on recreating
            if (self.config.start_minimized):
                self.window.minimize()

        # Update Layout if it's changed.
        if self.layout_dirty:
            self.refresh()
            print("[GUI] Refreshing layout...")

        # HACK: On Windows, the window gets stuck as keep_on_top for some reason.
        self.window.keep_on_top_clear()

        # This is the main GUI loop. The code will halt here until the next event.
        event, values = self.window.read()

        # Update Values
        self.update_values(values)
        
        # React to Event
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            self.shutting_down = True
            print("[GUI] Closing application.")
            return False
        if event[0] == KEY_BTN_TEST:
            self.tracker_test_event(event[1])
        elif event[0] == KEY_BTN_SETUP:
            self.setup_tracker_preset(event[1])
        elif event == KEY_BTN_ADD_EXTERNAL:
            self.add_external_event(values[KEY_BTN_ADD_EXTERNAL])
        elif event == KEY_BTN_DEBUG:
            self.popup_debug_params()
        elif event == KEY_BTN_APPLY:
            self.restart_osc_event()
        elif event == KEY_BTN_THEME_RESET:
            if self.config.theme != DEFAULT_THEME:
                self.config.theme = DEFAULT_THEME
                sg.theme(self.config.theme)
                self.recreate_window()
        elif event == KEY_BTN_REFRESH:
            self.refresh_vr_event()
        elif event == KEY_OPEN_URL_HOME:
            webbrowser.open("https://hapticpancake.com/")
        elif event == KEY_OPEN_URL_DONATE:
            webbrowser.open("https://hapticpancake.com/donate")
        elif event == KEY_TIMER_REFRESH:
            if self.cache_force_refresh:
                print("[GUI] Forcing refresh of OSC status bar")
                # HACK: Work around status bar getting stuck on some setups
                cache_error = False
                if self.cache_osc_status_bar_color == self.theme_color_bad:
                    cache_error = True
                self.update_osc_status_bar(self.cache_osc_status_bar_text, cache_error, self.cache_server_apply_disabled)
                self.cache_force_refresh = False
            ## Quietly refresh on timer elapse
            self.refresh_vr_event(quiet_refresh=True)
            self.window.timer_start(TIMER_REFRESH_MS, key=KEY_TIMER_REFRESH, repeating=False)

        return True

    def popup_pick_address_preset(self, tracker_serial):
        """GUI to pick a tracker location preset"""
        button_size = 12
        location_layout = [
            [sg.Push(),
             sg.Button('Head', key=KEY_PRESET_HEAD, size=button_size, tooltip=f"Head, including VR headset\nParameter: {PRESET_ADDRESSES[KEY_PRESET_HEAD]}"),
             sg.Push()],
            [self.small_vertical_space()],
            [sg.Button('Left Elbow', key=KEY_PRESET_ELBOW_LEFT, size=button_size, tooltip=f"Left elbow, arm, or shoulder\nParameter: {PRESET_ADDRESSES[KEY_PRESET_ELBOW_LEFT]}"),
             sg.Push(),
             sg.Button('Chest', key=KEY_PRESET_CHEST, size=button_size, tooltip=f"Chest, upper body\nUse this when you have separate haptic devices for Chest and Hips\nParameter: {PRESET_ADDRESSES[KEY_PRESET_CHEST]}"),
             sg.Push(),
             sg.Button('Right Elbow', key=KEY_PRESET_ELBOW_RIGHT, size=button_size, tooltip=f"Right elbow, arm, or shoulder\nParameter: {PRESET_ADDRESSES[KEY_PRESET_ELBOW_RIGHT]}")],
            [self.small_vertical_space()],
            [sg.Push(),
             sg.Button('Hips + Chest', key=KEY_PRESET_HIPS_CHEST, size=button_size, tooltip=f"Chest and hips, full torso (combined into one)\nUse this when you only have one haptic device for Chest and Hips\nParameter: {PRESET_ADDRESSES[KEY_PRESET_HIPS_CHEST]}"),
             sg.Push()],
            [sg.Push(),
             sg.Text("(combines Hips and Chest to one device)"),
             sg.Push()],
            [self.small_vertical_space()],
            [sg.Push(),
             sg.Button('Hips', key=KEY_PRESET_HIPS, size=button_size, tooltip=f"Hips, belly, lower body\nUse this when you have separate haptic devices for Chest and Hips\nParameter: {PRESET_ADDRESSES[KEY_PRESET_HIPS]}"),
             sg.Push()],
            [self.small_vertical_space()],
            [sg.Button('Left Knee', key=KEY_PRESET_KNEE_LEFT, size=button_size, tooltip=f"Left knee, leg, thigh or shin\nParameter: {PRESET_ADDRESSES[KEY_PRESET_KNEE_LEFT]}"),
             sg.Push(),
             sg.Button('Right Knee', key=KEY_PRESET_KNEE_RIGHT, size=button_size, tooltip=f"Right knee, leg, thigh or shin\nParameter: {PRESET_ADDRESSES[KEY_PRESET_KNEE_RIGHT]}")],
            [self.small_vertical_space()],
            [sg.Button('Left Foot', key=KEY_PRESET_FOOT_LEFT, size=button_size, tooltip=f"Left foot / paw, ankle, lower leg\nParameter: {PRESET_ADDRESSES[KEY_PRESET_FOOT_LEFT]}"),
             sg.Push(),
             sg.Button('Right Foot', key=KEY_PRESET_FOOT_RIGHT, size=button_size, tooltip=f"Right foot / paw, ankle, lower leg\nParameter: {PRESET_ADDRESSES[KEY_PRESET_FOOT_RIGHT]}")],
        ]

        preset_layout = [
            [sg.Text(f"1.  Find your haptics device", font='_ 14')],
            [sg.Button('Identify', key=KEY_BTN_TEST, size=button_size, pad=((12,0),(0,0))),
             sg.Text("Click for a brief vibration pulse.")],
            [sg.Text('2.  Where do you wear this?', font='_ 14')],
            [sg.Frame("Pick a location:", layout=location_layout, expand_x=True, expand_y=True)],
            [sg.Text(f"Device: {tracker_serial}"), sg.Push(), sg.Cancel()],
        ]

        window = sg.Window("Set up haptics address", preset_layout, keep_on_top=True, finalize=True, modal=True, icon=WINDOW_ICON)
        # Py/FreeSimpleGUI doesn't have real modal windows, so set keep_on_top
        # to help avoid losing the dialog box.

        # Center window on mouse cursor
        loc_mid_x = window.size[0] / 2
        loc_mid_y = window.size[1] / 2
        mouse_loc = window.mouse_location()
        window.move(int(mouse_loc[0] - loc_mid_x), int(mouse_loc[1] - loc_mid_y))
        # Don't allow resizing
        window.set_resizable(False, False)

        # Close on Escape key
        window.bind("<Escape>", "-ESCAPE-")

        while True:
            # Wait for event
            event, values = window.read()
            if event in PRESET_ADDRESSES:
                window.close()
                return PRESET_ADDRESSES[event]
            elif event == KEY_BTN_TEST:
                self.tracker_test_event(tracker_serial)
            else:
                window.close()
                return None

    def popup_debug_params(self):
        """GUI to pick a tracker location preset"""
        if self.debug_popup:
            # Don't try to open twice
            return

        self.debug_popup = DebugAddressPopup()
        # Separate object creation from event loop so object gets assigned
        # This is needed to pass parameters along
        self.debug_popup.show_popup()
        self.debug_popup = None

    def debug_params_received(self, address, value):
        if self.debug_popup:
            self.debug_popup.params_received(address, value)

    def setup_tracker_preset(self, tracker_serial):
        # Find value if possible
        address_widget = (KEY_OSC_ADDRESS, tracker_serial)
        if not self.window.key_is_good(address_widget):
            print(f"[GUI] Could not find address input widget for tracker {tracker_serial}!")

        new_address = self.popup_pick_address_preset(tracker_serial)
        if new_address:
            self.window[address_widget].update(new_address)
            # Run another iteration to make sure this gets applied
            self.window.write_event_value(KEY_SAVE_TO_CONFIG, "")

    def update_values(self, values):
        # print(f"Values: {values}")
        if values is None or values[KEY_REC_IP] is None:
            return

        for tracker in self.trackers:
            self.update_tracker_config(values, tracker)

        # Update app settings
        oldTheme = self.config.theme
        self.config.theme = values[KEY_THEME]
        if oldTheme != self.config.theme: # Theme change
            sg.theme(self.config.theme)
            self.recreate_window()

        old_start_with_steamvr = self.config.start_with_steamvr
        self.config.start_with_steamvr = values[KEY_START_WITH_STEAMVR]
        if old_start_with_steamvr != self.config.start_with_steamvr:
            self.setup_autostart_event(self.config.start_with_steamvr)

        self.config.start_minimized = values[KEY_START_MINIMIZED]

        # Update OSC Addresses
        self.config.server_type = LIST_SERVER_TYPE.index(values[KEY_SERVER_TYPE])
        self.config.server_osc_oscquery = values[KEY_SERVER_OSCQUERY]
        self.config.server_ip = values[KEY_REC_IP]
        try:
            self.config.server_port = int(values[KEY_REC_PORT])
        except ValueError:
            pass

        # Sync OSCQuery state
        self.update_oscquery_state()

        # Update vibration intensity and pattern
        self.update_pattern_config(values, VibrationPattern.PROXIMITY, KEY_PROXIMITY)
        self.update_pattern_config(values, VibrationPattern.VELOCITY, KEY_VELOCITY)
        self.config.no_data_enabled = values[KEY_NO_DATA_ENABLED]
        try:
            self.config.no_data_timeout = int(values[KEY_NO_DATA_TIMEOUT])
        except ValueError:
            pass
        # Sync spinbox enable state
        self.update_no_data_status(self.config.no_data_enabled)

        self.config.save()

    def update_tracker_config(self, values, tracker: str):
        # Update Tracker OSC Addresses
        key = (KEY_OSC_ADDRESS, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).set_address(values[key])

        # Update Tracker vibration
        key = (KEY_VIB_STR_OVERRIDE, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).set_vibration_multiplier(values[key])

        # Update Tracker battery threshold
        key = (KEY_BATTERY_THRESHOLD, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).set_battery_threshold((values[key]))

    def update_pattern_config(self, values, index: int, key: str):
        self.config.pattern_config_list[index].pattern = values[key + KEY_VIB_PATTERN]
        # If Spin value is backspaced, it can result in "" or "\n" - ignore this
        try:
            self.config.pattern_config_list[index].str_min = int(values[key + KEY_VIB_STR_MIN])
        except ValueError:
            pass
        try:
            self.config.pattern_config_list[index].str_max = int(values[key + KEY_VIB_STR_MAX])
        except ValueError:
            pass
        self.config.pattern_config_list[index].speed = int(values[key + KEY_VIB_SPEED])

class DebugAddressPopup:
    def __init__(self):
        """GUI to show parameter addresses and values"""
        button_size = 6
        self.timer_active = False
        self.param_list = {}
        self.debug_table = sg.Table([], headings=["Address", "Value"], justification='left', key=KEY_DEBUG_TBL_ADDRESS, enable_events=True, expand_x = True, expand_y = True, col_widths=[25, 5], auto_size_columns=False, select_mode=sg.TABLE_SELECT_MODE_BROWSE)
        # Set a specific column width to show more of address

        self.debug_autorefresh_chkbox = sg.Checkbox("Auto-refresh",
            default=True, key=KEY_DEBUG_CHK_AUTOREFRESH, enable_events=True,
            tooltip="Automatically refresh list of addresses and values.", pad=0)
        self.debug_filter_input = sg.InputText('haptic', key=KEY_DEBUG_INPUT_FILTER, size=25, expand_x=True)

        self.debug_stats = sg.Text('Refresh to see addresses')

        self.debug_copy_button = sg.Button("Copy Row", key=KEY_DEBUG_BTN_COPY, tooltip="Copy selected Address and Value to clipboard.", disabled=True)

        self.debug_layout = [
            [sg.Text("Filter:"),
             self.debug_filter_input,
             sg.Button("Refresh", key=KEY_DEBUG_BTN_REFRESH, size=button_size, tooltip="Refresh list of addresses and values.")],
             [self.debug_autorefresh_chkbox,
              sg.Push(),
              self.debug_copy_button,
              sg.Button("Clear", key=KEY_DEBUG_BTN_CLEAR, size=button_size, tooltip="Clear list of known addresses.")],
            [self.debug_table],
            [sg.HSep()],
            [self.debug_stats,
             sg.Push(),
             sg.Sizegrip()],
        ]

    @property
    def autorefresh_active(self):
        return self.debug_autorefresh_chkbox.get()

    def clear(self):
        self.param_list = {}
        # Preemptively clear selection too
        self.debug_table.update(select_rows=[])
        self.refresh()

    def copy_row(self):
        selected_rows = self.debug_table.get()
        if not len(selected_rows):
            return

        # Get selected row text (assume first row if multiple are selected)
        selected_row = self.debug_table.Values[selected_rows[0]]
        print(f"[DebugAddress] Copying row to clipboard: {selected_row}")
        # NOTE: On Linux, Tkinter requires the app to stay running to keep text
        # Modern desktop environments resolve this with clipboard managers.
        sg.clipboard_set(selected_row)

    def params_received(self, address, value):
        self.param_list[address] = value

    def refresh(self):
        ## Intentionally out of order to test sorting
        #self.param_list["/avatar/parameter/TestIndex"] = 3
        #self.param_list["/avatar/parameter/HapticChest"] = 0.3
        #self.param_list["/avatar/parameter/HapticHips"] = 0.3567465434
        #self.param_list["/avatar/parameter/WillGiveYouUp"] = False
        #self.param_list["/avatar/parameter/WillLetYouDown"] = False
        #self.param_list["/avatar/parameter/WillRunAroundAndDesertYou"] = False
        #self.param_list["/avatar/parameter/PineappleOnPizza"] = True

        filter_text = self.debug_filter_input.get().casefold()
        # Find addresses by matching substring
        param_list_filtered = [(k, v) for k, v in self.param_list.items() if filter_text in k.casefold()]
        # A-Z
        param_list_filtered.sort()

        # Get selected rows
        selected_rows = self.debug_table.get()
        selected_addr_text = None
        if len(selected_rows):
            # Check first selected row
            selected_addr_text = self.debug_table.Values[selected_rows[0]][0]

        # Update
        self.debug_table.update(param_list_filtered)
        self.debug_stats.update(f"{len(param_list_filtered)} matching addresses, {len(self.param_list)} total")

        # Restore selected rows
        if selected_addr_text:
            # Find new index
            try:
                # Find index of first matching address
                new_row_index = [row[0] for row in self.debug_table.Values].index(selected_addr_text)
                # Wrap in list (only a single item)
                self.debug_table.update(select_rows=[new_row_index])
            except ValueError:
                # No value found
                pass

        # Refresh again if enabled
        self.schedule_autorefresh()

    def run_loop(self):
        while True:
            # Wait for event
            event, values = self.window.read()
            if event == KEY_DEBUG_BTN_CLEAR:
                self.clear()
                self.refresh()
            elif event == KEY_DEBUG_BTN_COPY:
                self.copy_row()
            elif event == KEY_DEBUG_CHK_AUTOREFRESH:
                if self.autorefresh_active:
                    self.refresh()
            elif event == KEY_DEBUG_BTN_REFRESH:
                self.refresh()
            elif event == KEY_DEBUG_TBL_ADDRESS:
                self.update_select_status()
            elif event == KEY_DEBUG_TIMER_REFRESH:
                self.timer_active = False
                if self.autorefresh_active:
                    self.refresh()
            else:
                self.window.close()
                return None

    def schedule_autorefresh(self):
        if self.autorefresh_active and not self.timer_active:
            self.timer_active = True
            self.window.timer_start(DEBUG_TIMER_REFRESH_MS, key=KEY_DEBUG_TIMER_REFRESH, repeating=False)

    def show_popup(self):
        self.window = sg.Window("Debug server input", self.debug_layout, keep_on_top=True, finalize=True, modal=True, icon=WINDOW_ICON, use_default_focus=False)
        # Py/FreeSimpleGUI doesn't have real modal windows, so set keep_on_top
        # to help avoid losing the dialog box.

        # Center window on mouse cursor
        loc_mid_x = self.window.size[0] / 2
        loc_mid_y = self.window.size[1] / 2
        mouse_loc = self.window.mouse_location()
        self.window.move(int(mouse_loc[0] - loc_mid_x), int(mouse_loc[1] - loc_mid_y))
        # Allow resizing
        self.window.set_resizable(True, True)
        # Lock in current window size as minimum
        self.window.set_min_size(self.window.size)
        # Expand from minimum size in X and Y direction
        self.window.size = (self.window.size[0] + 100, self.window.size[1] + 100)

        # Make it easy to clear default filter
        self.debug_filter_input.update(select=True)
        self.debug_filter_input.set_focus()

        # Close on Escape key
        self.window.bind("<Escape>", "-ESCAPE-")

        self.schedule_autorefresh()

        self.run_loop()

    def update_select_status(self):
        """Update status of Copy Row button based on row selection"""
        self.debug_copy_button.update(disabled=not len(self.debug_table.get()))
