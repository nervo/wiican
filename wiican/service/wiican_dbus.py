# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2010 J. Félix Ontañón
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors : J. Félix Ontañón <fontanon@emergya.es>
# 
###

import os
import dbus, dbus.service, dbus.exceptions
from wminput import WMInputLauncher

from wiican.mapping import MappingValidator

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
WC_AVAILABLE = 3
WC_WIIMOTE_DISCOVERING = 4
WC_WIIMOTE_CONNECTED = 7

class WiicanDBus(dbus.service.Object):
    """A D-Bus service which allows to manage wiimote connections and track the wiimote connection states"""
    
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
        self.__check_uinput_present()

        if bluez_manager.ListAdapters():
            self.status = self.status | WC_BLUEZ_PRESENT
            self.StatusChanged(self.status)
            return True

        if self.status & WC_BLUEZ_PRESENT:
            self.status = self.status ^ WC_BLUEZ_PRESENT
            self.StatusChanged(self.status)

        return False

    def __check_uinput_present(self):
        # FIXME: Checking the wminput way, it may be a better way ...
        for uinput_filename in ['/dev/uinput', '/dev/input/uinput',
                '/dev/misc/uinput']:
            if os.access(uinput_filename, os.W_OK):
                self.status = self.status | WC_UINPUT_PRESENT
                self.StatusChanged(self.status)
                return True
            
        if self.status & WC_UINPUT_PRESENT:
            self.status = self.status ^ WC_UINPUT_PRESENT
            self.StatusChanged(self.status)
        return False

    def __plug_cb(self, udi):
        bus = dbus.SystemBus()
        device_dbus_obj = bus.get_object(HAL_URI, udi)
        properties = device_dbus_obj.GetAllProperties(dbus_interface=HAL_DEVICE_IFACE)

        if properties.has_key('input.product') and 'Nintendo Wiimote' in \
                properties['input.product']:
            self.wiimote_udi = udi
            self.status = self.status | WC_WIIMOTE_DISCOVERING
            self.StatusChanged(self.status)

    def __unplug_cb(self, udi):
        if self.wiimote_udi == udi and (self.status & WC_WIIMOTE_DISCOVERING):
            self.status = self.status ^ WC_WIIMOTE_DISCOVERING
            self.StatusChanged(self.status)

    @dbus.service.method(WIICAN_URI, out_signature='i')
    def GetStatus(self):
        """Get the current status as defined in the StatusChanged signal.

        Returns:
            an integer representing the current status

        """

        self.__check_uinput_present()
        return self.status

    @dbus.service.method(WIICAN_URI, in_signature='sb')
    def ConnectWiimote(self, config_file, daemon):
        """Request a wiimote connection using the config_file as mapping.

        In order to allow connections a bluetooth adaptor must be available, 
        the uinput module must be loaded and no other connection could be in 
        use (3 - WC_AVAILABLE status, check the StatusChanged signal for more info).

        The bluetooth adaptor connection changes are auto-discovered.
        By now, the uinput module load/unload it's only discovered at service 
        start and at bluetooth adaptor connection changes too. So the best
        it's to ensure that module it's loaded before launching the service.

        The daemon mode sets the connection for waiting indefinitely for 
        pressing 1+2 (not daemon mode only wait for 3 seconds) and trying to 
        reconnect if wiimote it's disconnected.

        Parameters:
        config_file - a string with the absolute path to mapping config file
        daemon - a boolean to set the daemon mode

        Potential Errors:
        Not uinput module present
        Not bluetooth adapter present
        A wiimote connection still in use (disconnect first)
        Mapping validation error
        """

        self.__check_uinput_present()
        if not self.status & WC_UINPUT_PRESENT:
            raise dbus.exceptions.DBusException('Not uinput module present')
        elif not self.status & WC_BLUEZ_PRESENT:
            raise dbus.exceptions.DBusException('Not bluetooth adapter present')
        elif self.status & WC_WIIMOTE_DISCOVERING:
            raise dbus.exceptions.DBusException('Disconnect wiimote first')
        else:
            if config_file:
                validator = MappingValidator()
                validator.validate_file(config_file, False)
                if validator.validation_errors:
                    raise dbus.exceptions.DBusException('Mapping validation error')
                    return

            self.__wminput = WMInputLauncher(config_file, daemon)
            self.__wminput.start()

    @dbus.service.method(WIICAN_URI)
    def DisconnectWiimote(self):
        """Close the wiimote connection or do nothing if no connection in use"""
        
        self.__wminput.stop()
        
    @dbus.service.method(WIICAN_URI)
    def Quit(self):
        """Exit wiican dbus service"""
        
        self.mainloop.quit()

    @dbus.service.signal(WIICAN_URI, signature='i')
    def StatusChanged(self, status):
        """Emitted when the status of the connection changes.
        All states have numerical values, as defined here:

        0 - WC_DISABLED
            No bluetooth adaptor available and uinput module it's not loaded.
            Wiimote connection could not be performed.

        1 - WC_BLUEZ_PRESENT
            Bluetooth adaptor available, nor uinput module. 
            Wiimote connection could not be performed.

        2 - WC_UINPUT_PRESENT
            The uinput module it's loaded, no bluetooth device available. 
            Wiimote connection could not be performed.

        3 - WC_AVAILABLE
            Bluetooth adaptor available, uinput module loaded.
            Wiimote connection could be performed.

        7 - WC_WIIMOTE_CONNECTED
            Wiimote connection in use.
            Disconnect first to make a new connection.

        Parameters:
        status - an integer indicating the new status
        """

        pass

if __name__ == '__main__':
    import gobject
    from dbus.mainloop.glib import DBusGMainLoop

    def status_cb(status):
        print 'Wiican status:', status

    DBusGMainLoop(set_as_default=True)
    loop = gobject.MainLoop()

    wiican = WiicanDBus(loop)

    bus = dbus.SessionBus()
    bus.add_signal_receiver(status_cb, dbus_interface='org.gnome.Wiican', 
            signal_name='StatusChanged')

    loop.run()
