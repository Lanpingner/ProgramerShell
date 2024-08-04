from gi.repository import GLib
from abstracts.StatusIndicator import StatusIndicator
from share.decoratos import register_function


class CurrentWindowIndicator(StatusIndicator):
    def __init__(self):
        super().__init__("utilities-system-monitor-symbolic", "Mem: ")
        self.label.set_text("".ljust(45, " "))
        register_function("hypr-activewindow", self.update_with_data)

    def update_with_data(self, data=None):
        if data is not None:
            if data["type"] == "activewindow":
                GLib.idle_add(
                    self._safe_update_label,
                    (str(data["data"]).split(",", 1)[1][:40].ljust(45, " ")),
                )
            # self.label.set_text(data["type"])
        return True  # Return True to keep the timeout active
