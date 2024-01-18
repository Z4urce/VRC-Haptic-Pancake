import PySimpleGUI as sg
import webbrowser

from config import AppConfig
from pattern import VibrationPattern

WINDOW_NAME = "Haptic Pancake Bridge v0.2.0"

KEY_REC_IP = '-REC-IP-'
KEY_REC_PORT = '-REC-PORT-'
KEY_BTN_APPLY = '-BTN-APPLY-'
KEY_BTN_REFRESH = '-BTN-REFRESH'
KEY_VIB_STR = '-VIB-STR-'
KEY_VIB_PATTERN = '-VIB-PATTERN-'
KEY_OPEN_URL = '-OPENURL'
KEY_OSC_STATUS_BAR = '-OSC-STATUS-BAR-'
KEY_LAYOUT_TRACKERS = '-LAYOUT-TRACKERS-'
KEY_OSC_ADDRESS = '-ADDRESS-OF-'
KEY_BTN_TEST = '-BTN-TEST'




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
            [sg.Text("Vibration Intensity:"),
             sg.Slider(range=(1, 100), size=(31, 10), default_value=self.config.global_vibration_intensity,
                       orientation='horizontal', key=KEY_VIB_STR, enable_events=True)],
            [sg.Text("Vibration Pattern:", size=14),
             sg.Drop(VibrationPattern.VIB_PATTERN_LIST, self.config.global_vibration_pattern,
                     k=KEY_VIB_PATTERN, size=37, readonly=True, enable_events=True)],
            [self.small_vertical_space()],
            [sg.Text('Trackers found:', font='_ 14')],
            [self.tracker_frame],
        ]

    @staticmethod
    def small_vertical_space():
        return sg.Text('', font=('AnyFont', 1), auto_size_text=True)

    def tracker_row(self, tracker_id, tracker_serial, tracker_model):
        string = f"⚫ {tracker_serial} {tracker_model}"
        default_text = self.config.tracker_to_osc[tracker_serial] \
            if tracker_serial in self.config.tracker_to_osc else "/avatar/parameters/..."
        print(f"[GUI] Adding tracker: {string}")
        layout = [[sg.Text(string, pad=(0, 0))],
                  [sg.Text(" "), sg.Text("OSC Address:"),
                   sg.InputText(default_text, k=(KEY_OSC_ADDRESS, tracker_serial), enable_events=True, size=32,
                                tooltip="OSC Address"),
                   sg.Button("Test", k=(KEY_BTN_TEST, tracker_id), tooltip="Send a 200ms pulse to the tracker")]]

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
        if values is None or values[KEY_VIB_STR] is None:
            return

        # Update Tracker OSC Addresses
        for tracker in self.trackers:
            key = (KEY_OSC_ADDRESS, tracker)
            if key in values:
                self.config.tracker_to_osc[tracker] = values[key]

        # Update OSC Addresses
        self.config.osc_address = values[KEY_REC_IP]
        self.config.osc_receiver_port = int(values[KEY_REC_PORT])

        # Update vibration intensity and pattern
        self.config.global_vibration_intensity = int(values[KEY_VIB_STR]) if KEY_VIB_STR in values else 0
        self.config.global_vibration_pattern = values[KEY_VIB_PATTERN]
        self.config.save()
