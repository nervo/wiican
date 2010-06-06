import dbus, dbus.service, dbus.exceptions
from wminput import WMInputLauncher

WIICAN_URI = 'org.gnome.Wiican'
WIICAN_PATH = '/org/gnome/Wiican'

DBUS_URI = 'org.freedesktop.DBus'
DBUS_PATH = '/org/freedesktop/DBus'

HAL_URI = 'org.freedesktop.Hal'
HAL_DEVICE_IFACE = 'org.freedesktop.Hal.Device'

BLUEZ_PATH = '/'
BLUEZ_URI = 'org.bluez'
BLUEZMANAGER_IFACE = 'org.bluez.Manager'

HAL_URI = 'org.freedesktop.Hal'
HAL_DEVICE_IFACE = 'org.freedesktop.Hal.Device'
HAL_MANAGER_URI = 'org.freedesktop.Hal.Manager'
HAL_MANAGER_PATH = '/org/freedesktop/Hal/Manager'

WC_DISABLED = 0
WC_BLUEZ_PRESENT = 1
WC_UINPUT_PRESENT = 2
WC_WIIMOTE_DISCOVERING = 4

class Wiican(dbus.service.Object):
    __dbus_object_path__ = WIICAN_PATH

    def __init__(self, loop):
        self.bus = dbus.SessionBus()
        self.mainloop = loop
        self.status = 0
        self.wiimote_udi = 0
        self.wminput = None
        
        dbus.service.Object.__init__(self, dbus.service.BusName(WIICAN_URI, 
            bus=self.bus), self.__dbus_object_path__)

        # Setup bluetooth
        bus = dbus.SystemBus()
        obj = bus.get_object (DBUS_URI, DBUS_PATH)
        bus_interface = dbus.Interface(obj, DBUS_URI)
    
        if BLUEZ_URI in bus_interface.ListNames():
            bus.add_signal_receiver(self.__bluez_discover,
                dbus_interface=BLUEZMANAGER_IFACE, signal_name='AdapterAdded')
            bus.add_signal_receiver(self.__bluez_discover,
                dbus_interface=BLUEZMANAGER_IFACE, signal_name='AdapterRemoved')

            self.__bluez_discover(None)

        else:
            bus.add_signal_receiver(self.__wait_for_bluez, 
                dbus_interface=DBUS_URI, signal_name='NameOwnerChanged')

        # Check for uinput module
        self.__check_uinput_present()

        # Setup HAL
        hal_manager_obj = bus.get_object(HAL_URI, HAL_MANAGER_PATH)
        hal_manager = dbus.Interface(hal_manager_obj, HAL_MANAGER_URI)
        hal_manager.connect_to_signal('DeviceAdded', self.__plug_cb)
        hal_manager.connect_to_signal('DeviceRemoved', self.__unplug_cb)

    def __wait_for_bluez(self, names, old_owner, new_owner):
        if BLUEZ_URI in names:
            bus = dbus.SystemBus()
            bus.add_signal_receiver(self.__bluez_discover,
                dbus_interface=BLUEZMANAGER_IFACE, signal_name='AdapterAdded')
            bus.add_signal_receiver(self.__bluez_discover,
                dbus_interface=BLUEZMANAGER_IFACE, signal_name='AdapterRemoved')

            self.__bluez_discover(None)

    def __bluez_discover(self, bt_adapter):
        obj = dbus.SystemBus().get_object(BLUEZ_URI, BLUEZ_PATH)
        bluez_manager = dbus.Interface(obj, dbus_interface=BLUEZMANAGER_IFACE)

        if bluez_manager.ListAdapters():
            self.StatusChanged(self.status | WC_BLUEZ_PRESENT)
            return True

        self.StatusChanged(self.status ^ WC_BLUEZ_PRESENT)    
        return False

    def __check_uinput_present(self):
        # FIXME: There must be a better and pythonic way to check it
        mod_fp = open('/proc/modules')
        modules = mod_fp.read()
        mod_fp.close()
        if 'uinput' in modules:
            self.StatusChanged(self.status | WC_UINPUT_PRESENT)
            return True
        else:
            self.StatusChanged(self.status ^ WC_UINPUT_PRESENT)
            return False

    def __plug_cb(self, udi):
        bus = dbus.SystemBus()
        device_dbus_obj = bus.get_object(HAL_URI, udi)
        properties = device_dbus_obj.GetAllProperties(dbus_interface=HAL_DEVICE_IFACE)

        if properties.has_key('input.product') and 'Nintendo Wiimote' in \
                properties['input.product']:
            self.wiimote_udi = udi
            self.StatusChanged(self.status | WC_WIIMOTE_DISCOVERING)

    def __unplug_cb(self, udi):
        if self.wiimote_udi == udi:
            self.StatusChanged(self.status ^ WC_WIIMOTE_DISCOVERING)

    @dbus.service.method(WIICAN_URI, out_signature='i')
    def GetStatus(self):
        return self.status

    @dbus.service.method(WIICAN_URI, in_signature='sb')
    def ConnectWiimote(self, config_file, daemon):
        self.__check_uinput_present()
        if not self.status & WC_UINPUT_PRESENT:
            raise dbus.exceptions.DBusException('Not uinput module present')
        elif not self.status & WC_BLUEZ_PRESENT:
            raise dbus.exceptions.DBusException('Not bluetooth adapter present')
        elif self.status & WC_WIIMOTE_DISCOVERING:
            raise dbus.exceptions.DBusException('Disconnect wiimote first')
        else:
            self.__wminput = WMInputLauncher(config_file, daemon)
            self.__wminput.start()

    @dbus.service.method(WIICAN_URI)
    def DisconnectWiimote(self):
        self.__wminput.stop()
        
    @dbus.service.method(WIICAN_URI)
    def Quit(self):
        self.mainloop.quit()

    @dbus.service.signal(WIICAN_URI, signature='i')
    def StatusChanged(self, status):
        self.status = status

if __name__ == '__main__':
    import gobject
    from dbus.mainloop.glib import DBusGMainLoop

    def status_cb(status):
        print 'Wiican status:', status

    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()

    wiican = Wiican(loop)
 
    bus = dbus.SessionBus()
    bus.add_signal_receiver(status_cb, dbus_interface='org.gnome.Wiican', 
            signal_name='StatusChanged')
    
    loop.run()
