import gi
import json
import hashlib
from service.datacollector import BatteryStatus, info, DataCollector
import socket
import os
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
from indicators.BatteryIndicator import BatteryIndicator
from indicators.MemoryIndicator import MemoryIndicator
from indicators.ClockIndicator import ClockIndicator
from indicators.CPUIndicator import CPUIndicator
from indicators.NetworkIndicator import NetworkIndicator


# Load configuration
config_file_path = 'config.json'
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

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


display = Gdk.Display.get_default()
n_screens = display.get_n_monitors()

class ShellWindow():
    def __init__(self, screen, indicators_config, position) -> None:
        self.indicators_config = indicators_config
        
        self.window = Gtk.Window()
        self.window.set_default_size(600, 30)
        
        self.sidebar_window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.sidebar_window.set_default_size(200, 400)
        
        self.setupWindow()
        self.setupSidebar()

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.init_for_window(self.sidebar_window)
        
        GtkLayerShell.auto_exclusive_zone_enable(self.window)

        if position == 'top':
            GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.TOP, 1)
        else:
            GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.BOTTOM, 1)

        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.LEFT, 1)
        GtkLayerShell.set_anchor(self.window, GtkLayerShell.Edge.RIGHT, 1)

        GtkLayerShell.set_anchor(self.sidebar_window, GtkLayerShell.Edge.BOTTOM, 1)
        GtkLayerShell.set_anchor(self.sidebar_window, GtkLayerShell.Edge.TOP, 1)
        GtkLayerShell.set_anchor(self.sidebar_window, GtkLayerShell.Edge.RIGHT, 1)
        
        GtkLayerShell.set_monitor(self.window, screen)
        GtkLayerShell.set_monitor(self.sidebar_window, screen)
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

        self.window.get_style_context().add_class("window")

        self.window.show_all()
        self.window.connect('destroy', Gtk.main_quit)
    
    def setupSidebar(self):
        # Add some sample content to the sidebar
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sidebar_box.set_margin_top(5)
        sidebar_box.set_margin_bottom(5)
        sidebar_box.set_margin_start(10)
        sidebar_box.set_margin_end(10)
        sidebar_label = Gtk.Label(label="Sidebar Content")
        sidebar_box.pack_start(sidebar_label, True, True, 0)

        self.sidebar_window.add(sidebar_box)
        self.sidebar_window.hide()

        # Toggle the sidebar visibility when the button is clicked
        def on_toggle_button_clicked(button):
            if self.sidebar_window.is_visible():
                self.sidebar_window.hide()
            else:
                self.sidebar_window.show_all()

        self.toggle_button.connect("clicked", on_toggle_button_clicked)

    def setupWindow(self):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox.set_margin_top(5)
        hbox.set_margin_bottom(5)
        hbox.set_margin_start(10)
        hbox.set_margin_end(10)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(1000)

        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)

        # Index label
        self.index_label = Gtk.Label()
        hbox.pack_start(self.index_label, False, False, 0)
        hbox.pack_start(stack_switcher, False, False, 0)

        def on_stack_notify(stack, param):
            visible_child_name = stack.get_visible_child_name()
            self.index_label.set_text(f"Page: {visible_child_name}")

        self.stack.connect("notify::visible-child", on_stack_notify)

        # Add indicators to stack
        pages = {
            '1': [('cpu', 'start'), ('network', 'center'), ('clock', 'end')],
            '2': [('network', 'center')],
            '3': [('memory', 'end')]
        }

        for page_num, indicators in pages.items():
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            for indicator_type, position in indicators:
                indicator = create_indicator(indicator_type, self.indicators_config[indicator_type])
                if indicator:
                    if position == 'start':
                        box.pack_start(indicator, False, False, 0)
                    elif position == 'center':
                        box.set_center_widget(indicator)
                    elif position == 'end':
                        box.pack_end(indicator, False, False, 0)
            self.stack.add_titled(box, page_num, f"Page {page_num}")

        hbox.pack_end(self.stack, True, True, 0)

        # Create a button to toggle the sidebar
        self.toggle_button = Gtk.Button(label="Menu")
        hbox.pack_end(self.toggle_button, False, False, 0)

        self.window.add(hbox)
    
    

    def getWindow(self):
        return self.window

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
    metrics_thread = DataCollector()
    metrics_thread.daemon = True
    metrics_thread.start()
    selected_screens = config.get('screens', 'all')
    windows = []
    if selected_screens == 'all':
        screens_to_use = range(n_screens)
    else:
        screens_to_use = selected_screens

    for screen in screens_to_use:
        if int(screen) < n_screens:
            pass    
        windows.append(ShellWindow(display.get_monitor(int(screen)), config['indicators'], config['position']))

    Gtk.main()

    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    if "--monitors" in sys.argv:
        monitors()
    if sys.argv.__len__() == 1:
        print("Run Main")
        main()


