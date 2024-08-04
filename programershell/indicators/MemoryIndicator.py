from gi.repository import GLib
from abstracts.StatusIndicator import StatusIndicator
from share.decoratos import register_function


class MemoryIndicator(StatusIndicator):
    def __init__(self):
        super().__init__("utilities-system-monitor-symbolic", "Mem: ")
        register_function("memory_percent_value", self.update_wth_data)

    def update_wth_data(self, data=None):
        if data is not None:
            self.label.set_text(f"{data['data']}%")
        return True  # Return True to keep the timeout active
