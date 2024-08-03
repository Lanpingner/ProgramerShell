import gi

gi.require_version("Gtk", "3.0")
import sys

try:
    gi.require_version("GtkLayerShell", "0.1")
except ValueError:
    import sys

    raise RuntimeError(
        "\n\n"
        + "If you haven't installed GTK Layer Shell, you need to point Python to the\n"
        + "library by setting GI_TYPELIB_PATH and LD_LIBRARY_PATH to <build-dir>/src/.\n"
        + "For example you might need to run:\n\n"
        + "GI_TYPELIB_PATH=build/src LD_LIBRARY_PATH=build/src python3 "
        + " ".join(sys.argv)
    )

from gi.repository import Gtk, GtkLayerShell, GLib, Gdk


def main():
    from loader import startup

    startup()
    Gtk.main()

    loop = GLib.MainLoop()
    loop.run()


if __name__ == "__main__":
    if sys.argv.__len__() == 1:
        print("Run Main")
        main()
