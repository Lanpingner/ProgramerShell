from gi.repository import GLib
from service.datacollector import info
from abstracts.StatusIndicator import StatusIndicator
from share.decoratos import register_function


class CurrentWindowIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__("utilities-system-monitor-symbolic", "Mem: ", update_interval)
        self.label.set_text("".ljust(45, " "))
        register_function("hypr", self.update_with_data)

    def update_with_data(self, data=None):
        if data is not None:
            if data["type"] == "activewindow":
                GLib.idle_add(
                    self._safe_update_label,
                    (str(data["data"]).split(",", 1)[1][:40].ljust(45, " ")),
                )
            # self.label.set_text(data["type"])
        return True  # Return True to keep the timeout active
