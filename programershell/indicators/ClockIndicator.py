from gi.repository import GLib
from service.datacollector import info
from abstracts.StatusIndicator import StatusIndicator
import time
class ClockIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('moon', 'Time: ', update_interval)
        GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(time.strftime("%H:%M:%S"))
        return True
