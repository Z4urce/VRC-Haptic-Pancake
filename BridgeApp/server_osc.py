from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from server_base import ServerBase
from app_config import AppConfig
import threading
from tinyoscquery.queryservice import OSCQueryService
from tinyoscquery.utility import get_open_tcp_port, get_open_udp_port
# For pretty error messages
from zeroconf._exceptions import NonUniqueNameException
# For unique mDNS names
import string
import random

class VRChatOSCReceiver(ServerBase):
    def __init__(self, config: AppConfig, param_received_event, status_update):
        super().__init__(config, param_received_event, status_update)
        self.oscquery_server = None
        self.oscquery_server_suffix = None
        self.thread = None
        self.server = None
        self.srv_ip = None
        self.srv_http_port = None
        self.srv_osc_port = None
        self.srv_use_oscquery = None
        self.dispatcher = Dispatcher()

    def shutdown(self):
        if self.is_alive:
            self.print_status("Shutting down...", True, True, True)

            if self.oscquery_server:
                # HACK: tinyoscquery v0.1.3 relies on object deletion and doesn't fully stop
                # Use proper shutdown method when available, don't poke internals
                self.oscquery_server.http_server.shutdown()
                self.oscquery_server.http_server.server_close()
                self.oscquery_server.http_thread.join()
                del self.oscquery_server
                self.oscquery_server = None
                self.oscquery_server_suffix = None

            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
            self.server = None
            self.print_status("Shutdown completed.")

    def event_received(self, address, osc_value):
        try:
            float_value = float(osc_value)
            self.param_received_event(address, float_value)
        except ValueError:
            pass

    def run(self):
        # Don't double-start
        if self.is_alive:
            return

        # If OSCQuery is enabled, find ports
        if self.srv_use_oscquery:
            self.srv_http_port = get_open_tcp_port()
            self.srv_osc_port = get_open_udp_port()

        try:
            address = (self.srv_ip, self.srv_osc_port)
            self.server = osc_server.OSCUDPServer(address, self.dispatcher)
        except Exception as e:
            self.print_status(f"[ERROR] Port: {self.srv_osc_port} occupied.\n{e}", True)
            return

        # Launch OSCQuery server if enabled
        if self.srv_use_oscquery:
            # HACK: Try to ensure unique service name.
            #
            # mDNS requires unique names, and unfortunately, the zeroconf
            # library does not appear to provide a working way to only
            # broadcast to localhost.  This means anyone on the same network
            # can see if you're running Haptic Pancake and names will conflict.
            # (It also means if mDNS is blocked, no OSCQuery for you!)
            #
            # Pick a random 3-digit suffix to avoid conflicts.  Unfortunately
            # this means it's easier to open multiple copies of the bridge app
            # on the same computer without realizing it.  Please don't do that.

            service_name = "Haptic Pancake"
            for attempt in range(0, 5):
                # If somehow 5 attempts fail, may RNG have mercy on your soul.
                try:
                    # While possible to use a name without suffix at first,
                    # mDNS name conflict detection is.. um.. "best-effort",
                    # and will frequently not detect conflicts.  Always
                    # randomize the suffix.
                    self.oscquery_server_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
                    service_name = f"Haptic Pancake ({self.oscquery_server_suffix})"

                    self.oscquery_server = OSCQueryService(service_name, self.srv_http_port, self.srv_osc_port, self.srv_ip)
                    break
                except NonUniqueNameException:
                    self.print_status(f"[ERROR] Name '{service_name}' in use, randomizing...", True, True, True)

            if self.oscquery_server:
                # Advertise avatar parameter listening
                self.oscquery_server.advertise_endpoint("/avatar/parameters")
            else:
                self.print_status(f"[ERROR] Name '{service_name}' in use.  App already open?", True, True)
                self.oscquery_server = None
                self.server = None
                return

        self.dispatcher.map("/avatar/parameters/*", self.event_received)

        try:
            srv_address = f"{self.server.server_address[0]}:{self.server.server_address[1]}"
        except:
            srv_address = str(self.server.server_address)

        if self.srv_use_oscquery:
            if self.oscquery_server_suffix:
                oscquery_id = f"{self.srv_http_port} ({self.oscquery_server_suffix})"
            else:
                oscquery_id = self.srv_http_port
            self.print_status(f"OSC receiving on {srv_address}, OSCQuery: {oscquery_id}", True)
        else:
            self.print_status(f"OSC receiving on {srv_address}", True)

        self.server.serve_forever()

    @property
    def is_alive(self):
        return self.server is not None

    def start_server(self):
        self.print_status("Starting...", True, True, True)

        # Cache setting values for shutdown handling
        self.srv_ip = self.config.server_ip
        self.srv_http_port = None
        self.srv_osc_port = int(self.config.server_port)
        self.srv_use_oscquery = self.config.server_osc_oscquery

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def restart_server(self):
        self.print_status("Restarting...", True, True, True)
        self.shutdown()
        self.start_server()

    def print_status(self, text, update_status_bar=False, is_error=False, is_busy=False):
        print(f"[OSC] {text}")
        if update_status_bar:
            self.status_update(text, is_error, is_busy)
