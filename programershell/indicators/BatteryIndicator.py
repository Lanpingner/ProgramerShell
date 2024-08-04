from gi.repository import GLib
from service.datacollector import BatteryStatus
from abstracts.StatusIndicator import StatusIndicator
from share.decoratos import register_function


class BatteryIndicator(StatusIndicator):
    def __init__(self):
        super().__init__("battery-good-symbolic", "Battery: ")
        register_function("battery_percent_value", self.update_with_data_percent)

    def update_with_data_percent(self, data=None):
        if data is not None:
            self.label.set_text(f"{round(float(data['data']), 0)}%")
        return True
