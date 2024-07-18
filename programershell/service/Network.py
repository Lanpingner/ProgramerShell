from sdbus_block.networkmanager import (
    NetworkManager,
    NetworkDeviceGeneric,
    NetworkDeviceWireless,
    IPv4Config,
)
from share.decoratos import call_registered_functions
from sdbus import sd_bus_open_system
from threading import Thread
from time import sleep
from enum import Enum

class InterfaceType(Enum):
    WIFI = 1
    ETHERNET = 2

class InterfaceIP4Config():
    def __init__(self) -> None:
        self.ip: list[str] = []
        self.gateway: list[str] = []

    def __repr__(self) -> str:
        return "".join(self.ip).join(self.gateway)


class Interface():
    def __init__(self, type: InterfaceType, name: str) -> None:
        self.type: InterfaceType = type
        self.ip4: InterfaceIP4Config = InterfaceIP4Config()
        self.name = name

    def __repr__(self) -> str:
        return "".join(str(self.type.value)).join(str(self.ip4))

class EthernetInterface(Interface):
    pass

class WifiInterface(Interface):
    def __init__(self, type: InterfaceType, name: str) -> None:
        super().__init__(type, name)
        self.ssid: str = ""

class NetworkObject():
    def __init__(self) -> None:
        self.Interfaces: list[Interface] = []

    def PushObject(self, obj: Interface) -> None:
        for int in self.Interfaces:
            if str(int) == str(obj):
                return
        self.Interfaces.append(obj)

    def pushEthernetObject(self, interfacename: str, ip4s: list[str], gw: list[str]):
        pass

    def pushWifiObject(self, interfacename: str, ssid: str, ip4s: list[str], gw: list[str]):
        pass


class NetworkService(Thread):
    def __init__(self):
        super().__init__()
        self.Network: NetworkObject = NetworkObject()
    
    def run(self) -> None:
        system_bus = sd_bus_open_system()  # We need system bus
        nm = NetworkManager(system_bus)
        while True:
            devices_paths = nm.get_devices()
            new_ips = []
            for device_path in devices_paths:
                generic_device = NetworkDeviceGeneric(device_path, system_bus)
                #print(generic_device.device_type, generic_device.interface)
                if generic_device.device_type == 2:
                    pass
                    #print(NetworkDeviceWireless(device_path, system_bus).get_applied_connection()[0]['connection'])
                device_ip4_conf_path = generic_device.ip4_config
                if device_ip4_conf_path == '/':
                    continue
                else:
                    ip4_conf = IPv4Config(device_ip4_conf_path, system_bus)
                    for address_data in ip4_conf.address_data:
                        #print('     Ip Adress:', address_data['address'][1])
                        new_ips.append(address_data['address'][1])
            self.ip4s = new_ips
            call_registered_functions("updateip")
            sleep(1)
ns: NetworkService | None = None

def getNetworkService() -> NetworkService:
    global ns
    if ns is None:
        ns = NetworkService()
        ns.start()
    return ns
        
