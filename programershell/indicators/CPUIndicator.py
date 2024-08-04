from gi.repository import GLib
from abstracts.StatusIndicator import StatusIndicator
from share.decoratos import register_function


class CPUIndicator(StatusIndicator):
    def __init__(self):
        super().__init__("computer-symbolic", "CPU: ")
        register_function("cpu_usage_value", self.update_with_data)

    def update_with_data(self, data=None):
        if data is not None:
            self.label.set_text(f"{data['data']}%")
        return True
