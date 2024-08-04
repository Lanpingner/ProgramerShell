from threading import Thread
import psutil
import time
from enum import Enum
from share.decoratos import call_registered_functions


class BatteryStatus(Enum):
    NONE = 0
    CHARGING = 1
    DESC = 2
    FULL = 3


class Value:
    def __init__(self, tolerance: float = 0.1) -> None:
        self.tolerance = tolerance
        self._value: float = 0
        self.owner = None
        self.name = None
        self.last_update_cycle = 0
        self.max_none_update_cycle = 5

    def update(self, newvalue: float) -> bool:
        if abs(newvalue - self._value) >= self.tolerance:
            self._value = newvalue
            self.sendUpdate()
            return True
        if self.last_update_cycle == self.max_none_update_cycle:
            self.sendUpdate(log=False)
            self.last_update_cycle = 0
        else:
            self.last_update_cycle += 1
        return False

    def sendUpdate(self, log=True):
        call_registered_functions(
            self.get_formatted_name(), data={"data": self.get()}, log=log
        )

    def get(self) -> float:
        return self._value

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __get__(self, instance, owner):
        return self

    def get_formatted_name(self) -> str:
        return f"{self.owner.__name__.lower()}_{self.name}_value"


class CPU:
    usage: Value = Value(tolerance=2)


class Memory:
    percent: Value = Value(tolerance=0.5)
    used: Value = Value()
    total: Value = Value()


class Battery:
    percent: Value = Value()
    status: Value = Value(tolerance=0)


class CommonInfoObject:
    def __init__(self) -> None:
        self.CPU: CPU = CPU()
        self.VirtualMemory: Memory = Memory()
        self.SwapMemory: Memory = Memory()
        self.Battery: Battery = Battery()


class DataCollector(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.info = CommonInfoObject()

    def run(self) -> None:
        while True:
            virtual_memory = psutil.virtual_memory()
            self.info.VirtualMemory.percent.update(virtual_memory.percent)
            self.info.CPU.usage.update(psutil.cpu_percent(interval=1))
            battery = psutil.sensors_battery()
            if battery:
                self.info.Battery.percent.update(battery.percent)
                if battery.power_plugged:
                    self.info.Battery.status.update(BatteryStatus.CHARGING.value)
                else:
                    self.info.Battery.status.update(BatteryStatus.DESC.value)
            else:
                self.info.Battery.percent.update(0)
                self.info.Battery.status.update(BatteryStatus.NONE.value)
            time.sleep(1)
