import FreeSimpleGUI as sg
import webbrowser

from app_config import AppConfig, PatternConfig
from app_pattern import VibrationPattern

WINDOW_NAME = "Haptic Pancake Bridge v0.5.3a"

LIST_SERVER_TYPE = ["OSC (VRChat)", "WebSocket (Resonite)"]

KEY_SERVER_TYPE = '-SERVER-TYPE-'
KEY_REC_IP = '-REC-IP-'
KEY_REC_PORT = '-REC-PORT-'
KEY_BTN_APPLY = '-BTN-APPLY-'
KEY_BTN_REFRESH = '-BTN-REFRESH'
KEY_OPEN_URL = '-OPENURL'
KEY_OSC_STATUS_BAR = '-OSC-STATUS-BAR-'
KEY_LAYOUT_TRACKERS = '-LAYOUT-TRACKERS-'
KEY_OSC_ADDRESS = '-ADDRESS-OF-'
KEY_VIB_STR_OVERRIDE = '-VIB-STR-'
KEY_BTN_TEST = '-BTN-TEST-'
KEY_BTN_CALIBRATE = '-BTN-CALIBRATE-'
KEY_BATTERY_THRESHOLD = '-BATTERY-'

# Pattern Config
KEY_PROXIMITY = '-PROXY-'
KEY_VELOCITY = '-VELOCITY-'
# Pattern Settings
KEY_VIB_STR_MIN = '-VIB-STR-MIN-'
KEY_VIB_STR_MAX = '-VIB-STR-MAX-'
KEY_VIB_PATTERN = '-VIB-PTN-'
KEY_VIB_SPEED = '-VIB-SPD-'


class GUIRenderer:
    def __init__(self, app_config: AppConfig, tracker_test_event, restart_osc_event, refresh_trackers_event):
        sg.theme('DarkAmber')  # Add a touch of color
        self.tracker_test_event = tracker_test_event
        self.restart_osc_event = restart_osc_event
        self.refresh_trackers_event = refresh_trackers_event
        self.config = app_config
        self.shutting_down = False
        self.window = None
        self.trackers = []
        self.osc_status_bar = sg.Text('', key=KEY_OSC_STATUS_BAR)
        self.tracker_frame = sg.Column([], key=KEY_LAYOUT_TRACKERS)
        self.layout = []
        self.build_layout()

    def build_layout(self):
        proximity_frame = sg.Frame('Proximity Feedback', tooltip="Closer object means stronger vibration.",
                                   layout=self.build_pattern_setting_layout(
                                       KEY_PROXIMITY, VibrationPattern.VIB_PATTERN_LIST,
                                       self.config.pattern_config_list[VibrationPattern.PROXIMITY]))
        velocity_frame = sg.Frame('Velocity Feedback', tooltip="Faster object means stronger vibration",
                                  layout=self.build_pattern_setting_layout(
                                      KEY_VELOCITY, VibrationPattern.VIB_PATTERN_LIST,
                                      self.config.pattern_config_list[VibrationPattern.VELOCITY]))

        self.layout = [
            [sg.Text('Bridge settings:', font='_ 14')],
            [sg.Text("Server Type:"),
             sg.InputCombo(LIST_SERVER_TYPE, LIST_SERVER_TYPE[self.config.server_type], key=KEY_SERVER_TYPE)],
            [sg.Text("Address:", size=9),
             sg.InputText(self.config.server_ip, k=KEY_REC_IP, size=16, tooltip="IP Address. Default is 127.0.0.1"),
             sg.Text("Port:", tooltip="UDP Port. Default is 9001"),
             sg.InputText(self.config.server_port, key=KEY_REC_PORT, size=13),
             sg.Button("Apply", key=KEY_BTN_APPLY, tooltip="Apply and restart server.")],
            [sg.Text("Server status:"), self.osc_status_bar],
            [self.small_vertical_space()],
            [sg.Text('Haptic settings:', font='_ 14')],
            [proximity_frame, velocity_frame],
            [self.small_vertical_space()],
            [sg.Text('Trackers found:', font='_ 14')],
            [self.tracker_frame],
        ]

    @staticmethod
    def build_pattern_setting_layout(key: str, pattern_list: [str], pattern_config: PatternConfig):
        speed_tooltip = "Defines the speed of the Throb pattern"
        pattern_tooltip = VibrationPattern.VIB_PATTERN_TOOLTIP

        return [
            [sg.Text("Pattern:", tooltip=pattern_tooltip),
             sg.Drop(pattern_list, pattern_config.pattern, tooltip=pattern_tooltip,
                     k=key + KEY_VIB_PATTERN, size=15, readonly=True, enable_events=True)],
            [sg.Text("Strength:"),
             sg.Text("Min:", pad=0),
             sg.Spin([num for num in range(0, 101)], pattern_config.str_min, pad=0,
                     key=key + KEY_VIB_STR_MIN, enable_events=True),
             sg.Text("Max:", pad=0),
             sg.Spin([num for num in range(0, 101)], pattern_config.str_max, pad=0,
                     key=key + KEY_VIB_STR_MAX, enable_events=True)],
            [sg.Text("Speed:", size=6, tooltip=speed_tooltip),
             sg.Slider(range=(1, 32), size=(13, 10), default_value=pattern_config.speed, tooltip=speed_tooltip,
                       orientation='horizontal', key=key + KEY_VIB_SPEED, enable_events=True)],
        ]

    @staticmethod
    def small_vertical_space():
        return sg.Text('', font=('AnyFont', 1), auto_size_text=True)

    def tracker_row(self, tracker_id, tracker_serial, tracker_model):
        string = f"⚫ {tracker_serial} {tracker_model}"

        dev_config = self.config.get_tracker_config(tracker_serial)
        address = dev_config.address
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold

        multiplier_tooltip = "1.0 for Vive trackers\n150 for Tundra trackers\n200 for Vive Wand\n400 for Index c."

        print(f"[GUI] Adding tracker: {string}")
        layout = [[sg.Text(string, pad=(0, 0))],
                  [sg.Text(" "), sg.Text("Address:"),
                   sg.InputText(address, k=(KEY_OSC_ADDRESS, tracker_serial), enable_events=True, size=35,
                                tooltip="OSC Address or Resonite Address"),
                   sg.Button("Identify", k=(KEY_BTN_TEST, tracker_serial), tooltip="Send a 500ms pulse to the tracker")],
                  [sg.Text(" "),
                   sg.Text("Battery threshold:", tooltip="Disables vibration bellow this battery level"),
                   sg.Spin([num for num in range(0, 91)], battery_threshold, pad=0,
                           key=(KEY_BATTERY_THRESHOLD, tracker_serial), enable_events=True),
                   sg.Text("%", pad=0),
                   sg.VSeparator(),
                   sg.Text("Pulse multiplier:", tooltip=multiplier_tooltip, pad=0),
                   sg.InputText(vib_multiplier, k=(KEY_VIB_STR_OVERRIDE, tracker_serial), enable_events=True,
                                size=4,
                                tooltip="The haptic intensity for this tracker will be multiplied by this number"),
                   sg.Button("Calibrate", button_color='grey', disabled=True, key=(KEY_BTN_CALIBRATE, tracker_serial),
                             tooltip="Coming soon...")
                   ]]

        row = [sg.pin(sg.Col(layout, key=('-ROW-', tracker_id)))]
        return row

    def add_tracker(self, tracker_id, tracker_serial, tracker_model):
        if tracker_serial in self.trackers:
            print(f"[GUI] Tracker {tracker_serial} is already on the list. Skipping...")
            return

        row = [self.tracker_row(tracker_id, tracker_serial, tracker_model)]
        if self.window is not None:
            self.window.extend_layout(self.window[KEY_LAYOUT_TRACKERS], row)
        else:
            self.tracker_frame.layout(row)

        self.trackers.append(tracker_serial)

    def add_message(self, message):
        self.layout.append([sg.HSep()])
        self.layout.append([sg.Text(message, text_color='red')])

    def add_footer(self):
        cs_tooltip = "Coming soon..."
        self.layout.append([self.small_vertical_space()])
        self.layout.append([sg.Button("Refresh Tracker List", size=18, key=KEY_BTN_REFRESH),
                            sg.Button("Add Serial device", disabled=True, button_color='grey', tooltip=cs_tooltip),
                            sg.Button("Add Network device", disabled=True, button_color='grey', tooltip=cs_tooltip)])
        self.layout.append([sg.HSep()])
        self.layout.append(
            [sg.Text("Made by Z4urce", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL)])

    def update_osc_status_bar(self, message, is_error=False):
        text_color = 'red' if is_error else 'green'
        if self.window is None:
            self.osc_status_bar.DisplayText = message
            self.osc_status_bar.TextColor = text_color
            return
        if not self.shutting_down:
            try:
                self.osc_status_bar.update(message, text_color=text_color)
            except Exception as e:
                print("[GUI] Failed to update server status bar.")

    def run(self):
        if self.window is None:
            self.window = sg.Window(WINDOW_NAME, self.layout)

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
        if event == KEY_BTN_APPLY:
            self.restart_osc_event()
        if event == KEY_BTN_REFRESH:
            self.refresh_trackers_event()
        if event == KEY_OPEN_URL:
            webbrowser.open("https://github.com/Z4urce/VRC-Haptic-Pancake")

        return True

    def update_values(self, values):
        # print(f"Values: {values}")
        if values is None or values[KEY_REC_IP] is None:
            return

        for tracker in self.trackers:
            self.update_tracker_config(values, tracker)

        # Update OSC Addresses
        self.config.server_type = LIST_SERVER_TYPE.index(values[KEY_SERVER_TYPE])
        self.config.server_ip = values[KEY_REC_IP]
        self.config.server_port = int(values[KEY_REC_PORT])

        # Update vibration intensity and pattern
        self.update_pattern_config(values, VibrationPattern.PROXIMITY, KEY_PROXIMITY)
        self.update_pattern_config(values, VibrationPattern.VELOCITY, KEY_VELOCITY)
        self.config.save()

    def update_tracker_config(self, values, tracker: str):
        # Update Tracker OSC Addresses
        key = (KEY_OSC_ADDRESS, tracker)
        if key in values:
            self.config.get_tracker_config(tracker).address = values[key]

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
        self.config.pattern_config_list[index].str_min = int(values[key + KEY_VIB_STR_MIN])
        self.config.pattern_config_list[index].str_max = int(values[key + KEY_VIB_STR_MAX])
        self.config.pattern_config_list[index].speed = int(values[key + KEY_VIB_SPEED])
