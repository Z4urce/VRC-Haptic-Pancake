import FreeSimpleGUI as sg
import webbrowser

from app_config import AppConfig, PatternConfig
from app_pattern import VibrationPattern

WINDOW_NAME = "Haptic Pancake Bridge v0.8.0a"

# If changing order, also change update_oscquery_state()
LIST_SERVER_TYPE = ["OSC (VRChat)", "WebSocket (Resonite)"]
LIST_THEME = [] # Initialized in __init__

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
KEY_BTN_TEST = '-BTN-TEST-'
KEY_BTN_CALIBRATE = '-BTN-CALIBRATE-'
KEY_BTN_ADD_EXTERNAL = '-BTN-ADD-EXTERNAL-'
KEY_BATTERY_THRESHOLD = '-BATTERY-'
KEY_START_WITH_STEAMVR = '-START-WITH-STEAMVR-'
KEY_AUTOSTART_STATUS_BAR = '-AUTOSTART-STATUS-BAR-'
KEY_START_MINIMIZED = '-START-MINIMIZED-'
KEY_THEME = '-THEME-'
KEY_BTN_THEME_RESET = '-BTN-THEME-RESET-'

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

        self.config = app_config
        self.shutting_down = False
        self.window = None
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
        self.server_apply_btn = sg.Button("Apply", key=KEY_BTN_APPLY, tooltip="Apply and restart server.", disabled=self.cache_server_apply_disabled)

        self.layout = [
            [sg.Text('App settings:', font='_ 14')],
            [self.autostart_chkbox, sg.Push(), self.autostart_status_bar],
            [sg.Checkbox("Start minimized", default=self.config.start_minimized, key=KEY_START_MINIMIZED, enable_events=True)],
            [sg.Text("Theme:", justification='right', size=7),
             sg.InputCombo(LIST_THEME, self.config.theme, key=KEY_THEME, readonly=True, enable_events=True, tooltip="Change app theme.\nCAUTION: Some themes are hard to read.  Be ready to reset."),
             sg.Button("Reset", key=KEY_BTN_THEME_RESET, tooltip=f"Reset theme to default ({DEFAULT_THEME})")],
            [sg.Text('Server settings:', font='_ 14')],
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
            [self.small_vertical_space()],
            [sg.Text('Devices:', font='_ 14'), self.tracker_status_bar, sg.Push(), sg.Button("Refresh", key=KEY_BTN_REFRESH)],
            # add_external_button],
            [self.tracker_frame],
            [sg.HSep()],
            [sg.Text("Made by BIT FOX DEN / Zelus", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL_HOME), sg.Push(),
             sg.Text("Enjoy Haptic Pancake?  Consider donating", enable_events=True, font='Default 8 underline', key=KEY_OPEN_URL_DONATE),
             sg.Sizegrip()],
        ]

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
                          enable_events=True, size=36,
                          tooltip="OSC Address or Resonite Address"),
             sg.Button("Identify", k=(KEY_BTN_TEST, tracker_serial),
                       tooltip="Send a 500ms pulse to the tracker")],
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

    def update_autostart_status(self, vr_ready, is_bundled):
        if not vr_ready:
            unavailable = True
            message = "SteamVR closed (open to apply changes)"
        elif not is_bundled:
            unavailable = False
            message = "SteamVR running (app unbundled)"
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

    def refresh(self):
        self.tracker_frame.contents_changed()
        self.tracker_frame.set_vscroll_position(1)
        self.window.refresh()
        self.layout_dirty = False


    def create_window(self):
        self.window = sg.Window(WINDOW_NAME, self.layout, keep_on_top=False, finalize=True, alpha_channel=1, icon=b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABhWlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpVIrDhYVcchQnezgB+JYqlgEC6Wt0KqDyaVf0KQhSXFxFFwLDn4sVh1cnHV1cBUEwQ8QZwcnRRcp8X9NoUWMB8f9eHfvcfcOEOplpppdEUDVLCMZi4qZ7Kroe0UvBjEEPyYlZurx1GIaruPrHh6+3oV5lvu5P0efkjMZ4BGJI0w3LOIN4tlNS+e8TxxkRUkhPieeMOiCxI9clx1+41xossAzg0Y6OU8cJBYLHSx3MCsaKvEMcUhRNcoXMg4rnLc4q+Uqa92TvzCQ01ZSXKc5ihiWEEcCImRUUUIZFsK0aqSYSNJ+1MU/0vQnyCWTqwRGjgVUoEJq+sH/4He3Zn56ykkKRIHuF9v+GAN8u0CjZtvfx7bdOAG8z8CV1vZX6sDcJ+m1thY6Avq3gYvrtibvAZc7wPCTLhlSU/LSFPJ54P2MvikLDNwC/jWnt9Y+Th+ANHW1fAMcHALjBcped3l3T2dv/55p9fcD3S9y0apk9h0AAAAGYktHRAD/AP8A/6C9p5MAAAAJcEhZcwAACxMAAAsTAQCanBgAAAAHdElNRQfoCxYXCzDoJVaPAAACuElEQVQ4y2WTTW8bdRDGfzO767f1xnGcJiSNVNoKqMoJgRBCwifuIHFFuSDRTwDi2CNfgC/gGxfElV6ockEISAJBiAJ5KVnqxk7idbx+ie39DwcngaqH0Wj0HJ756ZmRjz7940Ym0nCe1DMVnArZRbn/d+85bcMJ6744GqrUzYFimIAamMF5P8GCAC1GqAMDlFk3qItKQ9WsrmaoGd32LjYeMeg0edj4mOP9Hzj4/ku2v77PJO3MtPZj1GYmYlb31c1ch2ct5uZW6XZikpN9Rr02v377BenRNsuvvkfa2sUP5wlKFbJhDy1FmAm+GpiD6XkfRFGDfD7infc/p9XcobTwGbmoRpq2sKBI8VqNXjemUCijAr6YXa2kCL74RHOrEORYufkW5vk4haJlOAQFyDLUAAeqzhBn5IOQwMsxGfUo5MqMBwm++IjLmPQTovk1PFFGyVPCygpqhphdIBiUS4t0zg5ZWrqL84RcWL2KraTgVPEWb5KmLQIvT+bsWYThIKF1+BO9XpPDg+9YufU2raPfqCy/zOnJHvlyFcmVyMhYq65h/yGAOGA64cmjBxzHW/Tbf5Ec/c5Z6xFh+RphtESvfUAn3mFh+Q5yEbuYoZc3oAbVxZc4T2KiuRcYnP7N3dc/JCzVZjpGLiiyv/kVl6bqDPnk3o51ksc0n25SrFwn85TxdIRXiBi7Mc5Tpm5CYX6F5uGP5Mo1BoMON974AK8YzRCycUpn9yHd5i9M0xO6/2xzGm9ynsSEpRrZ8Ixee4+9b+5TrqzSP96buV8ieA5eefMeMh7Re/IzleqLyGSEOkcn3iKJt+i3/qR2612GpzGlcBFPfdSBL8bG/MLtulMhfO06mQoWBLMIRXCesnZn+sxnLtkUTzww2/AxWw+8fMOJ1NUv4Lzn39lXIVOu5kAFJ7rhnK3/C07bcJ2GHOyzAAAAAElFTkSuQmCC')

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
        elif event == KEY_BTN_ADD_EXTERNAL:
            self.add_external_event(values[KEY_BTN_ADD_EXTERNAL])
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
            # Quietly refresh on timer elapse
            self.refresh_vr_event(quiet_refresh=True)
            self.window.timer_start(TIMER_REFRESH_MS, key=KEY_TIMER_REFRESH, repeating=False)

        return True

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
