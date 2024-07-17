import gi
import time
import threading
import json
import os
import hashlib
from service.datacollector import BatteryStatus, info, DataCollector
from service.Network import NetworkService

gi.require_version('Gtk', '3.0')
import sys
try:
    gi.require_version('GtkLayerShell', '0.1')
except ValueError:
    import sys
    raise RuntimeError('\n\n' +
        'If you haven\'t installed GTK Layer Shell, you need to point Python to the\n' +
        'library by setting GI_TYPELIB_PATH and LD_LIBRARY_PATH to <build-dir>/src/.\n' +
        'For example you might need to run:\n\n' +
        'GI_TYPELIB_PATH=build/src LD_LIBRARY_PATH=build/src python3 ' + ' '.join(sys.argv))

from gi.repository import Gtk, GtkLayerShell, GLib, Gdk

from abstracts.StatusIndicator import StatusIndicator

# Load configuration
config_file_path = 'config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

class MemoryIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('utilities-system-monitor-symbolic', 'Mem: ', update_interval)
        GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(f'{info.VirtualMemory.percent}%')
        return True  # Return True to keep the timeout active

class CPUIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('computer-symbolic', 'CPU: ', update_interval)
        GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(f'{info.CPU.usage}%')
        return True

class ClockIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('moon', 'Time: ', update_interval)
        GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(time.strftime("%H:%M:%S"))
        return True

class NetworkIndicator(StatusIndicator):
    def __init__(self, update_interval):
        super().__init__('emblem-synchronizing-symbolic', 'IP: ', update_interval)
        self.network = NetworkService()
        self.network.start()
        GLib.timeout_add_seconds(update_interval, self.update)

    def update(self):
        self.label.set_text(" ".join(self.network.ip4s))
        return True

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

def create_indicator(indicator_type, config):
    if indicator_type == 'memory' and config['enabled']:
        return MemoryIndicator(config['update_interval'])
    elif indicator_type == 'cpu' and config['enabled']:
        return CPUIndicator(config['update_interval'])
    elif indicator_type == 'clock' and config['enabled']:
        return ClockIndicator(config['update_interval'])
    elif indicator_type == 'battery' and config['enabled']:
        return BatteryIndicator(config['update_interval'])
    elif indicator_type == 'network' and config['enabled']:
        return NetworkIndicator(config['update_interval'])
    else:
        return None

def create_bar_for_screen(screen, indicators_config, position):
    window = Gtk.Window()
    window.set_default_size(600, 30)
    print(window.get_screen().get_resolution())
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox.set_margin_top(5)
    hbox.set_margin_bottom(5)
    hbox.set_margin_start(10)
    hbox.set_margin_end(10)

    indicators = [
        create_indicator('memory', indicators_config['memory']),
        create_indicator('cpu', indicators_config['cpu']),
        create_indicator('clock', indicators_config['clock']),
        create_indicator('battery', indicators_config['battery'])
    ]

    for indicator in indicators:
        if indicator:
            hbox.pack_end(indicator, False, False, 0)

    # Create a button to toggle the sidebar
    toggle_button = Gtk.Button(label="Menu")
    hbox.pack_end(toggle_button, False, False, 0)
    hbox.set_center_widget(create_indicator('network', indicators_config['network']))
    window.add(hbox)

    # Create the sidebar window
    sidebar_window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    sidebar_window.set_default_size(200, 400)
    sidebar_window.set_position(Gtk.WindowPosition.CENTER)
    sidebar_window.set_decorated(False)  # Remove window decorations
    sidebar_window.set_transient_for(window)
    sidebar_window.set_type_hint(Gdk.WindowTypeHint.DOCK)

    # Add some sample content to the sidebar
    sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    sidebar_box.set_margin_top(5)
    sidebar_box.set_margin_bottom(5)
    sidebar_box.set_margin_start(10)
    sidebar_box.set_margin_end(10)
    sidebar_label = Gtk.Label(label="Sidebar Content")
    sidebar_box.pack_start(sidebar_label, True, True, 0)

    sidebar_window.add(sidebar_box)
    sidebar_window.hide()

    # Toggle the sidebar visibility when the button is clicked
    def on_toggle_button_clicked(button):
        if sidebar_window.is_visible():
            sidebar_window.hide()
        else:
            sidebar_window.show_all()

    toggle_button.connect("clicked", on_toggle_button_clicked)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.init_for_window(sidebar_window)
    GtkLayerShell.auto_exclusive_zone_enable(window)

    if position == 'top':
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP, 1)
    else:
        GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.BOTTOM, 1)

    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.LEFT, 1)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.RIGHT, 1)

    GtkLayerShell.set_anchor(sidebar_window, GtkLayerShell.Edge.BOTTOM, 1)
    GtkLayerShell.set_anchor(sidebar_window, GtkLayerShell.Edge.TOP, 1)
    GtkLayerShell.set_anchor(sidebar_window, GtkLayerShell.Edge.RIGHT, 1)
    GtkLayerShell.set_monitor(window, screen)
    # Add CSS styling
    css = b"""
    .window {
        background-color: #2E3440;
        color: #D8DEE9;
        font-family: Arial, sans-serif;
    }

    .label {
        font-size: 14px;
    }

    .hbox {
        padding: 5px;
    }
    """

    style_provider = Gtk.CssProvider()
    style_provider.load_from_data(css)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    window.get_style_context().add_class("window")

    window.show_all()
    window.connect('destroy', Gtk.main_quit)
    return window

# Start the metrics collection thread
metrics_thread = DataCollector()
metrics_thread.daemon = True
metrics_thread.start()

# Get the list of screens

display = Gdk.Display.get_default()
n_screens = display.get_n_monitors()
#monitors = []
#for m in range(n_screens):
#    monitors.append(display.get_monitor_geometry(m))
#print(monitors)

                    # Get the selected screens from config


def monitors():
    print("ID".center(10),"|", "Name".center(100),"|","MD5".ljust(40))
    for i in range(n_screens):
        print(str(i).center(10), 
              #display.get_monitor(i), 
              #display.get_monitor(i).get_display(),
              ##display.get_monitor(i).get_display().get_default_screen(),
              "|",
              str(f"{display.get_monitor(i).get_manufacturer()} {display.get_monitor(i).get_model()}").center(100),
              "|",
              str(hashlib.md5(str(f"{display.get_monitor(i).get_manufacturer()} {display.get_monitor(i).get_model()}").encode()).hexdigest()).ljust(40))

def main():
    selected_screens = config.get('screens', 'all')
    windows = []
    if selected_screens == 'all':
        screens_to_use = range(n_screens)
    else:
        screens_to_use = selected_screens

    for screen in screens_to_use:
        if int(screen) < n_screens:
            pass    
        windows.append(create_bar_for_screen(display.get_monitor(int(screen)), config['indicators'], config['position']))

    Gtk.main()

    loop = GLib.MainLoop()
    loop.run()
if __name__ == "__main__":
    if "--monitors" in sys.argv:
        monitors()
    if sys.argv.__len__() == 1:
        print("Run Main")
        main()


