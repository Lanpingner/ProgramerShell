import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib

class NotificationServer(dbus.service.Object):
    def __init__(self, bus_name, object_path='/org/freedesktop/Notifications'):
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.freedesktop.Notifications', in_signature='susssasa{sv}i', out_signature='u')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        print(f"Notification received from {app_name}:")
        print(f"  Summary: {summary}")
        print(f"  Body: {body}")
        print(app_name, replaces_id, app_icon, summary, body, actions, hints)
        return 0

    @dbus.service.method('org.freedesktop.Notifications', in_signature='', out_signature='as')
    def GetCapabilities(self):
        return []

    @dbus.service.method('org.freedesktop.Notifications', in_signature='', out_signature='ssss')
    def GetServerInformation(self):
        return ("MyNotificationServer", "MyCompany", "1.0", "1.2")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName("org.freedesktop.Notifications", session_bus)
    server = NotificationServer(name)
    
    loop = GLib.MainLoop()
    print("Notification server is running...")
    loop.run()

if __name__ == "__main__":
    main()

