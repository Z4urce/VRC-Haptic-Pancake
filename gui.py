import PySimpleGUI as sg

import config
from config import AppConfig

WINDOW_NAME = "Haptic Feedback Bridge v0.1.0"

KEY_REC_IP = '-RECIP-'
KEY_REC_PORT = '-RECPORT-'
KEY_BTN_APPLY = '-BTNAPPLY-'
KEY_VIB_STR = '-VIBSTR-'

class GUIRenderer:
    def __init__(self, config: AppConfig, tracker_test_event, restart_osc_event):
        sg.theme('DarkAmber')  # Add a touch of color
        self.tracker_test_event = tracker_test_event
        self.restart_osc_event = restart_osc_event
        self.config = config
        self.window = None
        self.trackers = []
        self.layout = [
            [sg.Text('OSC Listener settings:', font='_ 14')],
            [sg.Text("Address:"), sg.InputText(self.config.osc_address, key=KEY_REC_IP, size=16), sg.Text("Port:"),
             sg.InputText(self.config.osc_receiver_port, key=KEY_REC_PORT, size=16),
             sg.Button("Apply", key=KEY_BTN_APPLY)],
            [sg.Text('Haptic settings:', font='_ 14')],
            [sg.Text("Vibration Intensity:"),
             sg.Slider(range=(1, 1000), size=(25, 10), default_value=self.config.vibration_intensity,
                       orientation='horizontal', key=KEY_VIB_STR)],
            [sg.Text('Trackers found:', font='_ 14')]
        ]

    def add_tracker(self, tracker_id, tracker_serial, tracker_model):
        self.trackers.append(tracker_serial)
        string = f"{tracker_serial} {tracker_model}"
        print(f"Adding tracker: {string}")
        self.layout.append(
            [sg.Text(string), sg.InputText('/avatar/parameters/...', key=f"ADDRESS_OF={tracker_serial}"),
             sg.Button("Test", key=f"TEST_ID={tracker_id}")])

    def add_message(self, message):
        self.layout.append([sg.Text('_' * 50)])
        self.layout.append([sg.Text(message, text_color='red')])

    def show_error_window(self, error_message):
        sg.popup_ok(error_message)

    def run(self):
        if self.window is None:
            self.window = sg.Window(WINDOW_NAME, self.layout)

        event, values = self.window.read()

        # Update Values
        self.update_values(values)

        # React to Event
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            print("Closing application.")
            return False
        if event.startswith("TEST_ID="):
            self.tracker_test_event(int(event.split("=")[1]))
        if event == KEY_BTN_APPLY:
            self.restart_osc_event()

        return True

    def update_values(self, values):
        if values is None or values[KEY_VIB_STR] is None:
            return

        # Update Tracker OSC Addresses
        for tracker in self.trackers:
            self.config.tracker_to_osc[tracker] = values[f"ADDRESS_OF={tracker}"]
            print(f"Tracker {tracker} has been set to {self.config.tracker_to_osc[tracker]}")

        # Update OSC Addresses
        self.config.osc_address = values[KEY_REC_IP]
        self.config.osc_receiver_port = int(values[KEY_REC_PORT])

        # Update vibration intensity
        self.config.vibration_intensity = int(values[KEY_VIB_STR]) if KEY_VIB_STR in values else 0
        print(f"Vibration has been set to {self.config.vibration_intensity}")
