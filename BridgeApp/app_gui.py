import FreeSimpleGUI as sg
import webbrowser

from app_config import AppConfig, PatternConfig
from app_pattern import VibrationPattern

WINDOW_NAME = "Haptic Pancake Bridge v0.7.0a"

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
KEY_BTN_ADD_EXTERNAL = '-BTN-ADD-EXTERNAL-'
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
    def __init__(self, app_config: AppConfig, tracker_test_event,
                 restart_osc_event, refresh_trackers_event, add_external_event):
        sg.theme('DarkAmber')
        self.tracker_test_event = tracker_test_event
        self.restart_osc_event = restart_osc_event
        self.refresh_trackers_event = refresh_trackers_event
        self.add_external_event = add_external_event

        self.config = app_config
        self.shutting_down = False
        self.window = None
        self.layout_dirty = False
        self.trackers = []
        self.osc_status_bar = sg.Text('', key=KEY_OSC_STATUS_BAR)
        self.tracker_frame = sg.Column([], key=KEY_LAYOUT_TRACKERS, scrollable=True, vertical_scroll_only=True, expand_y=True, size=(406,270))
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

    def device_row(self, tracker_serial, tracker_model, additional_layout, icon=None):
        if icon is None:
            icon = "⚫"

        string = f"{icon} {tracker_serial} {tracker_model}"

        dev_config = self.config.get_tracker_config(tracker_serial)
        address = dev_config.get_address_str()
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold

        multiplier_tooltip = "Additional strength multiplier\nCompensates for different trackers\n1.0 for default (Vive/Tundra Tracker)\n200 for Vive Wand\n400 for Index c."

        print(f"[GUI] Adding tracker: {string}")
        layout = [
            [sg.Text(string, pad=(0, 0))],
            [sg.Text(" "), sg.Text("Address:"),
             sg.InputText(address, k=(KEY_OSC_ADDRESS, tracker_serial),
                          enable_events=True, size=35,
                          tooltip="OSC Address or Resonite Address"),
             sg.Button("Identify", k=(KEY_BTN_TEST, tracker_serial),
                       tooltip="Send a 500ms pulse to the tracker")],
            additional_layout]

        row = [sg.pin(sg.Col(layout, key=('-ROW-', tracker_serial)))]
        return row

    def tracker_row(self, tracker_serial, tracker_model):
        dev_config = self.config.get_tracker_config(tracker_serial)
        vib_multiplier = dev_config.multiplier_override
        battery_threshold = dev_config.battery_threshold
        multiplier_tooltip = "The haptic intensity for this tracker will be multiplied by this number"

        tr = [sg.Text(" "),
              sg.Text("Battery threshold:", tooltip="Disables vibration bellow this battery level"),
              sg.Spin([num for num in range(0, 90)], battery_threshold, pad=0,
                      key=(KEY_BATTERY_THRESHOLD, tracker_serial), enable_events=True),
              sg.Text("%", pad=0),
              sg.VSeparator(),
              sg.Text("Pulse multiplier:", tooltip=multiplier_tooltip, pad=0),
              sg.InputText(vib_multiplier, k=(KEY_VIB_STR_OVERRIDE, tracker_serial), enable_events=True,
                           size=4, tooltip=multiplier_tooltip),
              sg.Button("Calibrate", button_color='grey', disabled=True, key=(KEY_BTN_CALIBRATE, tracker_serial),
                        tooltip="Coming soon...")]
        return self.device_row(tracker_serial, tracker_model, tr)

    def add_tracker(self, tracker_serial, tracker_model):
        row = [self.tracker_row(tracker_serial, tracker_model)]
        self.add_target(tracker_serial, tracker_model, row)

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

    def add_target(self, tracker_serial, tracker_model, layout):
        if tracker_serial in self.trackers:
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
        self.layout.append([sg.Text(message, text_color='red')])

    def add_footer(self):
        external_devices = ['Add', ['Emulated (Sound)::EMUSND', 'Emulated (Text)::EMUTXT',
                                    'Serial (COM port)::SERIALCOM', 'Network (Server)::NETWORK']]
        self.layout.append([self.small_vertical_space()])
        self.layout.append([sg.Button("Refresh Tracker List", size=18, key=KEY_BTN_REFRESH),
                            sg.ButtonMenu("Add External device", external_devices, key=KEY_BTN_ADD_EXTERNAL, disabled=True,
                                          tooltip="Add an external feedback device"), ])
        self.layout.append([sg.HSep()])
        self.layout.append(
            [sg.Text("Made by Zelus (Z4urce)", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL), sg.Sizegrip()])

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

    def refresh(self):
        self.tracker_frame.contents_changed()
        self.tracker_frame.set_vscroll_position(1)
        self.window.refresh()
        self.layout_dirty = True

    def run(self):
        if self.window is None:
            self.window = sg.Window(WINDOW_NAME, self.layout, keep_on_top=False, finalize=True, alpha_channel=0.9, icon=b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpVIrDhYVcchQnezgB+JYqlgEC6Wt0KqDyaVf0KQhSXFxFFwLDn4sVh1cnHV1cBUEwQ8QZwcnRRcp8X9NoUWMB8f9eHfvcfcOEOplpppdEUDVLCMZi4qZ7Kroe0UvBjEEPyYlZurx1GIaruPrHh6+3oV5lvu5P0efkjMZ4BGJI0w3LOIN4tlNS+e8TxxkRUkhPieeMOiCxI9clx1+41xossAzg0Y6OU8cJBYLHSx3MCsaKvEMcUhRNcoXMg4rnLc4q+Uqa92TvzCQ01ZSXKc5ihiWEEcCImRUUUIZFsK0aqSYSNJ+1MU/0vQnyCWTqwRGjgVUoEJq+sH/4He3Zn56ykkKRIHuF9v+GAN8u0CjZtvfx7bdOAG8z8CV1vZX6sDcJ+m1thY6Avq3gYvrtibvAZc7wPCTLhlSU/LSFPJ54P2MvikLDNwC/jWnt9Y+Th+ANHW1fAMcHALjBcped3l3T2dv/55p9fcD3S9y0apk9h0AAAAGYktHRAD/AP8A/6C9p5MAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfoCxYXCzDoJVaPAAACuElEQVQ4y2WTTW8bdRDGfzO767f1xnGcJiSNVNoKqMoJgRBCwifuIHFFuSDRTwDi2CNfgC/gGxfElV6ockEISAJBiAJ5KVnqxk7idbx+ie39DwcngaqH0Wj0HJ756ZmRjz7940Ym0nCe1DMVnArZRbn/d+85bcMJ6744GqrUzYFimIAamMF5P8GCAC1GqAMDlFk3qItKQ9WsrmaoGd32LjYeMeg0edj4mOP9Hzj4/ku2v77PJO3MtPZj1GYmYlb31c1ch2ct5uZW6XZikpN9Rr02v377BenRNsuvvkfa2sUP5wlKFbJhDy1FmAm+GpiD6XkfRFGDfD7infc/p9XcobTwGbmoRpq2sKBI8VqNXjemUCijAr6YXa2kCL74RHOrEORYufkW5vk4haJlOAQFyDLUAAeqzhBn5IOQwMsxGfUo5MqMBwm++IjLmPQTovk1PFFGyVPCygpqhphdIBiUS4t0zg5ZWrqL84RcWL2KraTgVPEWb5KmLQIvT+bsWYThIKF1+BO9XpPDg+9YufU2raPfqCy/zOnJHvlyFcmVyMhYq65h/yGAOGA64cmjBxzHW/Tbf5Ec/c5Z6xFh+RphtESvfUAn3mFh+Q5yEbuYoZc3oAbVxZc4T2KiuRcYnP7N3dc/JCzVZjpGLiiyv/kVl6bqDPnk3o51ksc0n25SrFwn85TxdIRXiBi7Mc5Tpm5CYX6F5uGP5Mo1BoMON974AK8YzRCycUpn9yHd5i9M0xO6/2xzGm9ynsSEpRrZ8Ixee4+9b+5TrqzSP96buV8ieA5eefMeMh7Re/IzleqLyGSEOkcn3iKJt+i3/qR2612GpzGlcBFPfdSBL8bG/MLtulMhfO06mQoWBLMIRXCesnZn+sxnLtkUTzww2/AxWw+8fMOJ1NUv4Lzn39lXIVOu5kAFJ7rhnK3/C07bcJ2GHOyzAAAAAElFTkSuQmCC')
            self.window.set_resizable(False, True)

        # Update Layout if it's changed.
        if self.layout_dirty:
            self.refresh()
            print('Refreshing layout...')
        
        # We make sure the layout update is called only when it's changed.
        self.layout_dirty = False

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
        if event == KEY_BTN_ADD_EXTERNAL:
            self.add_external_event(values[KEY_BTN_ADD_EXTERNAL])
        if event == KEY_BTN_APPLY:
            self.restart_osc_event()
        if event == KEY_BTN_REFRESH:
            self.refresh_trackers_event()
        if event == KEY_OPEN_URL:
            webbrowser.open("https://hapticpancake.com/")

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
        self.config.pattern_config_list[index].str_min = int(values[key + KEY_VIB_STR_MIN])
        self.config.pattern_config_list[index].str_max = int(values[key + KEY_VIB_STR_MAX])
        self.config.pattern_config_list[index].speed = int(values[key + KEY_VIB_SPEED])
