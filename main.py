#!/usr/bin/python

import sys
import dbus
import gobject
import pynotify

import wiistray

from defs import * 
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

pynotify.init("wiistray")

wiisystray = wiistray.WiimoteManager()
listen = wiistray.WiimoteListener()

bus = dbus.SystemBus()
bus.add_signal_receiver(wiisystray.enable, dbus_interface=BLUEZMANAGER_IFACE, 
                signal_name="AdapterAdded")
bus.add_signal_receiver(wiisystray.disable, dbus_interface=BLUEZMANAGER_IFACE,
                signal_name="AdapterRemoved")

hal_manager_obj = bus.get_object(HAL_URI, HAL_MANAGER_PATH)
hal_manager = dbus.Interface(hal_manager_obj, HAL_MANAGER_URI)

hal_manager.connect_to_signal("DeviceAdded", listen.plug_cb)
hal_manager.connect_to_signal("DeviceRemoved", listen.unplug_cb)

gobject.MainLoop().run()
