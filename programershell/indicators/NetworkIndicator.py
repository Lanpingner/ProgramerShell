from gi.repository import GLib
from abstracts.StatusIndicator import StatusIndicator
from share.decoratos import register_function


class NetworkIndicator(StatusIndicator):
    def __init__(self):
        super().__init__("emblem-synchronizing-symbolic", "IP: ")
        register_function("updateip", self.update_with_data)

    def update_with_data(self, data=None):
        if data is not None:
            self.label.set_text(
                " ".join([", ".join(i.ip4.ip) for i in data.Interfaces])
            )
        return True
