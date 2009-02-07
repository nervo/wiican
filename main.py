#!/usr/bin/python

import sys
import dbus
import gobject
import pynotify

import wiistray

from defs import * 
from dbus.mainloop.glib import DBusGMainLoop
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

wiimanager = wiistray.WiimoteManager()

bus = dbus.SystemBus()

bus.add_signal_receiver(wiimanager.enable, dbus_interface=BLUEZMANAGER_IFACE, 
                signal_name="AdapterAdded")
bus.add_signal_receiver(wiimanager.disable, dbus_interface=BLUEZMANAGER_IFACE,
                signal_name="AdapterRemoved")

hal_manager_obj = bus.get_object(HAL_URI, HAL_MANAGER_PATH)
hal_manager = dbus.Interface(hal_manager_obj, HAL_MANAGER_URI)
hal_manager.connect_to_signal("DeviceAdded", wiimanager.plug_cb)
hal_manager.connect_to_signal("DeviceRemoved", wiimanager.unplug_cb)

gobject.MainLoop().run()
