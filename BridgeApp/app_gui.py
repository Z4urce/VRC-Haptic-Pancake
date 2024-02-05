import PySimpleGUI as sg
import webbrowser

from app_config import AppConfig, PatternConfig
from app_pattern import VibrationPattern

WINDOW_NAME = "Haptic Pancake Bridge v0.4.0b"

KEY_REC_IP = '-REC-IP-'
KEY_REC_PORT = '-REC-PORT-'
KEY_BTN_APPLY = '-BTN-APPLY-'
KEY_BTN_REFRESH = '-BTN-REFRESH'
KEY_OPEN_URL = '-OPENURL'
KEY_OSC_STATUS_BAR = '-OSC-STATUS-BAR-'
KEY_LAYOUT_TRACKERS = '-LAYOUT-TRACKERS-'
KEY_OSC_ADDRESS = '-ADDRESS-OF-'
KEY_VIB_STR_OVERRIDE = '-VIB-STR-'
KEY_BTN_TEST = '-BTN-TEST'

# Pattern Config
KEY_PROXIMITY = '-PROXY-'
KEY_VELOCITY = '-VELOCITY-'
# Pattern Settings
KEY_VIB_INTENSITY = '-VIB-INT-'
KEY_VIB_PATTERN = '-VIB-PTN-'
KEY_VIB_SPEED = '-VIB-SPD-'


class GUIRenderer:
    def __init__(self, app_config: AppConfig, tracker_test_event, restart_osc_event, refresh_trackers_event):
        sg.theme('DarkAmber')  # Add a touch of color
        self.tracker_test_event = tracker_test_event
        self.restart_osc_event = restart_osc_event
        self.refresh_trackers_event = refresh_trackers_event
        self.config = app_config
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
            [sg.Text('OSC Listener settings:', font='_ 14')],
            [sg.Text("Address:"),
             sg.InputText(self.config.osc_address, k=KEY_REC_IP, size=16, tooltip="IP Address. Default is 127.0.0.1"),
             sg.Text("Port:", tooltip="UDP Port. Default is 9001"),
             sg.InputText(self.config.osc_receiver_port, key=KEY_REC_PORT, size=16),
             sg.Button("Apply", key=KEY_BTN_APPLY, tooltip="Apply and restart OSC server.")],
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
        return [
            [sg.Text("Pattern:"),
             sg.Drop(pattern_list, pattern_config.pattern,
                     k=key + KEY_VIB_PATTERN, size=14, readonly=True, enable_events=True)],
            [sg.Text("Intensity:", size=7),
             sg.Slider(range=(1, 100), size=(12, 10), default_value=pattern_config.intensity,
                       orientation='horizontal', key=key + KEY_VIB_INTENSITY, enable_events=True)],
            [sg.Text("Speed:", size=7),
             sg.Slider(range=(1, 64), size=(12, 10), default_value=pattern_config.speed,
                       orientation='horizontal', key=key + KEY_VIB_SPEED, enable_events=True)],
        ]

    @staticmethod
    def small_vertical_space():
        return sg.Text('', font=('AnyFont', 1), auto_size_text=True)

    def tracker_row(self, tracker_id, tracker_serial, tracker_model):
        string = f"⚫ {tracker_serial} {tracker_model}"

        default_osc_address = self.config.tracker_to_osc[tracker_serial] \
            if tracker_serial in self.config.tracker_to_osc else "/avatar/parameters/..."
        default_vib_int_override = self.config.tracker_to_vib_int_override[tracker_serial] \
            if tracker_serial in self.config.tracker_to_vib_int_override else 1.0

        print(f"[GUI] Adding tracker: {string}")
        layout = [[sg.Text(string, pad=(0, 0))],
                  [sg.Text(" "), sg.Text("OSC Address:"),
                   sg.InputText(default_osc_address, k=(KEY_OSC_ADDRESS, tracker_serial), enable_events=True, size=32,
                                tooltip="OSC Address"),
                   sg.Button("Test", k=(KEY_BTN_TEST, tracker_id), tooltip="Send a 500ms pulse to the tracker")],
                  [sg.Text(" "), sg.Text("Intensity multiplier:"),
                   sg.InputText(default_vib_int_override, k=(KEY_VIB_STR_OVERRIDE, tracker_serial), enable_events=True,
                                size=32,
                                tooltip="The haptic intensity for this tracker will be multiplied by this number")]]

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
        self.layout.append([self.small_vertical_space()])
        self.layout.append([sg.Button("Refresh Tracker List", key=KEY_BTN_REFRESH)])
        self.layout.append([sg.HSep()])
        self.layout.append(
            [sg.Text("Made by Z4urce", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL)])

    def update_osc_status_bar(self, message, is_error=False):
        text_color = 'red' if is_error else 'green'
        if self.window is None:
            self.osc_status_bar.DisplayText = message
            self.osc_status_bar.TextColor = text_color
            return
        self.osc_status_bar.update(message, text_color=text_color)

    def run(self):
        if self.window is None:
            self.window = sg.Window(WINDOW_NAME, self.layout)

        event, values = self.window.read()

        # Update Values
        self.update_values(values)

        # React to Event
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
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
        if values is None:
            return

        # Update Tracker OSC Addresses
        for tracker in self.trackers:
            key = (KEY_OSC_ADDRESS, tracker)
            if key in values:
                self.config.tracker_to_osc[tracker] = values[key]

        # Update Tracker vibration
        for tracker in self.trackers:
            key = (KEY_VIB_STR_OVERRIDE, tracker)
            if key in values:
                try:
                    self.config.tracker_to_vib_int_override[tracker] = float(values[key])
                except ValueError:
                    pass  # Ignore the error for now

        # Update OSC Addresses
        self.config.osc_address = values[KEY_REC_IP]
        self.config.osc_receiver_port = int(values[KEY_REC_PORT])

        # Update vibration intensity and pattern
        self.update_pattern_config(values, VibrationPattern.PROXIMITY, KEY_PROXIMITY)
        self.update_pattern_config(values, VibrationPattern.VELOCITY, KEY_VELOCITY)
        self.config.save()

    def update_pattern_config(self, values, index: int, key: str):
        self.config.pattern_config_list[index].pattern = values[key + KEY_VIB_PATTERN]
        self.config.pattern_config_list[index].intensity = int(values[key + KEY_VIB_INTENSITY])
        self.config.pattern_config_list[index].speed = int(values[key + KEY_VIB_SPEED])
