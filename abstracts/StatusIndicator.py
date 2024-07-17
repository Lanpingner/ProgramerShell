from gi.repository import Gtk, GtkLayerShell, GLib, Gdk

class StatusIndicator(Gtk.Box):
    def __init__(self, icon_name, label_text, update_interval):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.icon: Gtk.Image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        self.label = Gtk.Label(label=label_text)
        self.pack_start(self.icon, False, False, 0)
        self.pack_start(self.label, False, False, 0)
        self.update_interval = update_interval
        #self.update()
    
    def updateIcon(self, icon_name):
        self.icon.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)

    def update(self):
        raise NotImplementedError("Subclasses should implement this method")
