from gi.repository import Gtk, GtkLayerShell, GLib, Gdk
from indicators.BatteryIndicator import BatteryIndicator
from indicators.MemoryIndicator import MemoryIndicator
from indicators.ClockIndicator import ClockIndicator
from indicators.CPUIndicator import CPUIndicator
from indicators.NetworkIndicator import NetworkIndicator
from indicators.CurrentWindow import CurrentWindowIndicator
from abstracts.StatusIndicator import StatusIndicator


def create_indicator(indicator_type, config, monitor_id) -> StatusIndicator | None:
    lres = None
    if indicator_type == "memory":
        lres = MemoryIndicator(config["update_interval"])
    elif indicator_type == "cpu":
        lres = CPUIndicator(config["update_interval"])
    elif indicator_type == "clock":
        lres = ClockIndicator(config["update_interval"])
    elif indicator_type == "battery":
        lres = BatteryIndicator(config["update_interval"])
    elif indicator_type == "network":
        lres = NetworkIndicator(config["update_interval"])
    elif indicator_type == "current_window":
        lres = CurrentWindowIndicator(config["update_interval"])
    else:
        return None
    if lres is not None:
        lres.monitor_id = monitor_id
        return lres
    else:
        return None


class ShellWindow:
    def __init__(self, screen, indicators_config, position) -> None:
        self.indicators_config = indicators_config
        self.screen = screen
        self.window = Gtk.Window()
        self.window.set_default_size(600, 30)

        self.sidebar_window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.sidebar_window.set_default_size(200, 400)

        self.setupWindow()
        self.setupSidebar()

        GtkLayerShell.init_for_window(self.window)
        GtkLayerShell.init_for_window(self.sidebar_window)

        GtkLayerShell.auto_exclusive_zone_enable(self.window)

        if position == "top":
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
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.window.get_style_context().add_class("window")

        self.window.show_all()
        self.window.connect("destroy", Gtk.main_quit)

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

        self.index_label = Gtk.Label()
        hbox.pack_start(self.index_label, False, False, 0)

        def on_stack_notify(stack, param):
            visible_child_name = stack.get_visible_child_name()
            self.index_label.set_text(f"Page: {visible_child_name}")

        self.stack.connect("notify::visible-child", on_stack_notify)

        # Add indicators to stack
        pages = {
            "1": [
                ("current_window", "start"),
                ("cpu", "start"),
                ("network", "center"),
                ("clock", "end"),
                ("cpu", "end"),
                ("memory", "end"),
                ("battery", "end"),
            ],
            "2": [],
            "3": [("memory", "end")],
        }

        for page_num, indicators in pages.items():
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            for indicator_type, position in indicators:
                indicator = create_indicator(
                    indicator_type, self.indicators_config[indicator_type], self.screen
                )
                if indicator is not None:
                    if position == "start":
                        box.pack_start(indicator, False, False, 0)
                    elif position == "center":
                        box.set_center_widget(indicator)
                    elif position == "end":
                        box.pack_end(indicator, False, False, 0)
            self.stack.add_titled(box, page_num, f"Page {page_num}")

        hbox.pack_end(self.stack, True, True, 0)

        # Create a button to toggle the sidebar
        self.toggle_button = Gtk.Button(label="Menu")
        hbox.pack_end(self.toggle_button, False, False, 0)

        self.window.add(hbox)

    def getWindow(self):
        return self.window
