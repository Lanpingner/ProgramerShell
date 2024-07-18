from gi.repository import GLib
from service.datacollector import info
from abstracts.StatusIndicator import StatusIndicator

class CPUIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('computer-symbolic', 'CPU: ', update_interval)
        GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(f'{info.CPU.usage}%')
        return True
