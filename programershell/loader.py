from gi.repository import Gdk, Gtk, GLib
from bar import ShellWindow
import json
import hashlib
from service.servicemanager import startServices

display = Gdk.Display.get_default()
n_screens = display.get_n_monitors()


config_file_path = "config.json"
with open(config_file_path, "r") as config_file:
    config = json.load(config_file)


def monitors():
    print("ID".center(10), "|", "Name".center(100), "|", "MD5".ljust(40))
    for i in range(n_screens):
        print(
            str(i).center(10),
            # display.get_monitor(i),
            # display.get_monitor(i).get_display(),
            ##display.get_monitor(i).get_display().get_default_screen(),
            "|",
            str(
                f"{display.get_monitor(i).get_manufacturer()} {display.get_monitor(i).get_model()}"
            ).center(100),
            "|",
            str(
                hashlib.md5(
                    str(
                        f"{display.get_monitor(i).get_manufacturer()} {display.get_monitor(i).get_model()}"
                    ).encode()
                ).hexdigest()
            ).ljust(40),
        )


def startup():
    startServices()
    selected_screens = config.get("screens", "all")
    windows = []
    if selected_screens == "all":
        screens_to_use = range(n_screens)
    else:
        screens_to_use = selected_screens

    for screen in screens_to_use:
        if int(screen) < n_screens:
            pass
        windows.append(
            ShellWindow(
                display.get_monitor(int(screen)),
                config["indicators"],
                config["position"],
            )
        )
