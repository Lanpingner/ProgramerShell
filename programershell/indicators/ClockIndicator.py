from gi.repository import GLib
from abstracts.StatusIndicator import StatusIndicator
import time
import datetime


class ClockIndicator(StatusIndicator):
    def __init__(self):
        super().__init__("moon", "Time: ")
        GLib.timeout_add_seconds(1, self.update)

    def update(self):
        self.label.set_text(
            f'{datetime.datetime.now().strftime("%Y-%m-%d")}\n{time.strftime("%H:%M:%S")}'
        )
        return True
