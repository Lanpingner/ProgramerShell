from threading import Thread
import psutil
import time
from enum import Enum

class BatteryStatus(Enum):
    NONE = 0
    CHARGING = 1 
    DESC = 2 
    FULL = 3

class CPU():
    def __init__(self) -> None:
        self.usage: float = 0

class Memory():
    def __init__(self) -> None:
        self.percent :float = 0
        self.used: float = 0
        self.total: float = 0

class Battery():
    def __init__(self) -> None:
        self.percent: float = 0
        self.status: BatteryStatus = BatteryStatus.NONE

class CommonInfoObject():
    def __init__(self) -> None:
        self.CPU = CPU()
        self.VirtualMemory = Memory()
        self.SwapMemory = Memory()
        self.Battery = Battery()

info = CommonInfoObject()

class DataCollector(Thread):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        global info
        while True:
            info.VirtualMemory.percent = psutil.virtual_memory().percent
            info.CPU.usage = psutil.cpu_percent(interval=1)
            battery = psutil.sensors_battery()
            info.Battery.percent = battery.percent if battery else 0 
            if battery.power_plugged:
                info.Battery.status = BatteryStatus.CHARGING
            else:
                info.Battery.status = BatteryStatus.DESC
            time.sleep(1)




