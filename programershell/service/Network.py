from sdbus_block.networkmanager import (
    NetworkManager,
    NetworkDeviceGeneric,
    NetworkDeviceWireless,
    IPv4Config,
    AccessPoint,
)
from sdbus import sd_bus_open_system
from threading import Thread
from time import sleep, time
from enum import Enum
from share.decoratos import call_registered_functions


class InterfaceType(Enum):
    ETHERNET = 1
    WIFI = 2


class InterfaceIP4Config:
    def __init__(self) -> None:
        self.ip: list[str] = []
        self.gateway: list[str] = []

    def __repr__(self) -> str:
        return f"IP: {', '.join(self.ip)}, Gateway: {', '.join(self.gateway)}"


class Interface:
    def __init__(self, type: InterfaceType, name: str) -> None:
        self.type: InterfaceType = type
        self.ip4: InterfaceIP4Config = InterfaceIP4Config()
        self.name = name

    def __repr__(self) -> str:
        return f"Type: {self.type.name}, Name: {self.name}, {self.ip4}"


class EthernetInterface(Interface):
    def __init__(self, name: str) -> None:
        super().__init__(InterfaceType.ETHERNET, name)


class WifiInterface(Interface):
    def __init__(self, name: str) -> None:
        super().__init__(InterfaceType.WIFI, name)
        self.ssid: str = ""

    def __repr__(self) -> str:
        return f"SSID: {self.ssid}, {super().__repr__()}"


class NetworkObject:
    def __init__(self) -> None:
        self.Interfaces: list[Interface] = []

    def PushObject(self, obj: Interface) -> None:
        for intf in self.Interfaces:
            if str(intf) == str(obj):
                return
        self.Interfaces.append(obj)

    def pushEthernetObject(self, interfacename: str, ip4s: list[str], gw: list[str]):
        eth_int = EthernetInterface(interfacename)
        eth_int.ip4.ip = ip4s
        eth_int.ip4.gateway = gw
        self.PushObject(eth_int)

    def pushWifiObject(
        self, interfacename: str, ssid: str, ip4s: list[str], gw: list[str]
    ):
        wifi_int = WifiInterface(interfacename)
        wifi_int.ssid = ssid
        wifi_int.ip4.ip = ip4s
        wifi_int.ip4.gateway = gw
        self.PushObject(wifi_int)


class NetworkService(Thread):
    def __init__(self):
        super().__init__()
        self.Network: NetworkObject = NetworkObject()
        self.last_network_state = None
        self.last_call_time = time()

    def has_state_changed(self):
        current_state = str(self.Network.Interfaces)
        if self.last_network_state != current_state:
            print(self.last_network_state, " -> ", current_state)
            self.last_network_state = current_state
            return True
        return False

    def added(self, data):
        print(data)

    def run(self) -> None:
        system_bus = sd_bus_open_system()  # We need system bus
        nm = NetworkManager(system_bus)
        while True:
            try:
                devices_paths = nm.get_devices()
                self.Network.Interfaces = []  # Reset the network interfaces list
                for device_path in devices_paths:
                    generic_device = NetworkDeviceGeneric(device_path, system_bus)
                    device_ip4_conf_path = generic_device.ip4_config
                    if device_ip4_conf_path == "/":
                        continue
                    else:
                        ip4_conf = IPv4Config(device_ip4_conf_path, system_bus)
                        ip_addresses = [
                            address_data["address"][1]
                            for address_data in ip4_conf.address_data
                        ]
                        gw = str(ip4_conf.gateway) if ip4_conf.gateway else "0.0.0.0"
                        gateways: list[str] = [gw]
                        if generic_device.device_type == InterfaceType.ETHERNET.value:
                            self.Network.pushEthernetObject(
                                generic_device.interface, ip_addresses, gateways
                            )
                        elif generic_device.device_type == InterfaceType.WIFI.value:
                            wifi_device = NetworkDeviceWireless(device_path, system_bus)
                            for l in wifi_device.get_all_access_points():
                                ap = AccessPoint(l, system_bus)
                                if str(l) == str(wifi_device.active_access_point):
                                    print("Active", ap.ssid)
                                else:
                                    print(ap.ssid)
                            # for l in wifi_device.get_all_access_points():
                            # ap = AccessPoint(l, system_bus)
                            # if str(l) == str(wifi_device.active_access_point):
                            #    print("Active", ap.ssid)
                            # else:
                            #    print(ap.ssid)
                            self.Network.pushWifiObject(
                                generic_device.interface,
                                "",
                                ip_addresses,
                                gateways,
                            )

                current_time = time()
                if (
                    self.has_state_changed()
                    or (current_time - self.last_call_time) >= 10
                ):
                    call_registered_functions("updateip", self.Network)
                    self.last_call_time = current_time

                sleep(1)
            except Exception as e:
                print(e)
                sleep(1)
