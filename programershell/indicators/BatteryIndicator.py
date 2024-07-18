from gi.repository import GLib
from service.datacollector import info, BatteryStatus
from abstracts.StatusIndicator import StatusIndicator

class BatteryIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('battery-good-symbolic', 'Battery: ', update_interval)
        GLib.timeout_add_seconds(update_interval, self.update)  # Update every 60 seconds

    def update(self):
        if info.Battery.status == BatteryStatus.CHARGING:
            self.updateIcon('emblem-synchronizing-symbolic')
        else:
            self.updateIcon('battery-good-symbolic')
        self.label.set_text(f'{round(info.Battery.percent, 0)}%')
        return True
