from gi.repository import GLib
from service.datacollector import info
from abstracts.StatusIndicator import StatusIndicator
from service.Network import getNetworkService
from share.decoratos import register_function


class NetworkIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__("emblem-synchronizing-symbolic", "IP: ", update_interval)
        self.network = getNetworkService()
        # GLib.timeout_add_seconds(update_interval, self.update)
        register_function("updateip", self.update)

    def update(self):
        self.label.set_text(" ".join(self.network.ip4s))
        return True
