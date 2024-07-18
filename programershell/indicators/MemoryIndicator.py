from gi.repository import GLib
from service.datacollector import info
from abstracts.StatusIndicator import StatusIndicator

class MemoryIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('utilities-system-monitor-symbolic', 'Mem: ', update_interval)
        #GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(f'{info.VirtualMemory.percent}%')
        return True  # Return True to keep the timeout active
