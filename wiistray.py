import sys
import os

import gtk
import pynotify
import gobject
import dbus
import subprocess
import threading
import signal

from defs import *
from notificator import Notificator

gtk.gdk.threads_init()

class BlueDiscover:
    def __init__(self):
	bus = dbus.SystemBus()
	bluezmanager = bus.get_object(BLUEZ_URI, BLUEZ_PATH) 
        self.__list_adapters = dbus.Interface(bluezmanager, 
                dbus_interface=BLUEZMANAGER_IFACE).ListAdapters

    def any_adapter(self):
	if self.__list_adapters():
            return True
        
        return False

class WiimoteListener:
    def __init__(self):
        self.__bus = dbus.SystemBus()
        self.__wiimote_udi = None
    
    def plug_cb(self, udi):
        device_dbus_obj = self.__bus.get_object(HAL_URI, udi)
        properties = device_dbus_obj.GetAllProperties(dbus_interface=HAL_DEVICE_IFACE)

        try:
            if "Nintendo Wiimote" in properties["input.product"]:
                self.__wiimote_udi = udi
                print "CONECTADO"
                Notificator().show_notification("Connected", "Press 1+2", icon=ICON_NOTIFY)
        except:
            pass

    def unplug_cb(self, udi):
        if self.__wiimote_udi == udi:
            print "DESCONECTADO"
            Notificator().show_notification("Disconnected", "Wiimote off", icon=ICON_NOTIFY)

class WiimoteManager:
    def __init__(self):
	self.__icon = gtk.StatusIcon()
        self.__bluediscover = BlueDiscover()
        self.__notificator = Notificator()
	self.__notificator.set_status_icon(self.__icon)
        self.__deploy_menus()

        adapter = self.__bluediscover.any_adapter()
	if adapter:
            self.enable(adapter)
        else:
            self.disable(adapter)

        self.__icon.connect("popup-menu", self.__icon_popupmenu_cb, None)
	self.__icon.set_visible(True)

    def enable(self, device):
        self.__icon.set_from_file(ICON_ON)
        self.__icon.set_tooltip('Right click for menu')

	for menu_item, enabled in self.__enabled_menu.items():
	    if enabled:
                menu_item.show()
            else:
                menu_item.hide()

    def disable(self, device):
	if not self.__bluediscover.any_adapter():
            self.__icon.set_from_file(ICON_OFF)
	    self.__icon.set_tooltip('Plug a bluetooth adapter')
	for menu_item, enabled in self.__disabled_menu.items():
	    if enabled:
                menu_item.show()
            else:
                menu_item.hide()

    def __deploy_menus(self):
        self.__menu = gtk.Menu()

        discover_item = gtk.CheckMenuItem("Discover wiimote")
        discover_item.connect("toggled", self.__discover_cb)
        self.__menu.append(discover_item)

        prefs_item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        prefs_item.connect("activate", self.__show_preferences_cb, None)
        self.__menu.append(prefs_item)

        nobluez_item = gtk.MenuItem("No bluetooth adapters")
        self.__menu.append(nobluez_item)

        sep_item = gtk.SeparatorMenuItem()
        sep_item.show()
        self.__menu.append(sep_item)

        about_item = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about_item.connect('activate', self.__about_cb, None)
        about_item.show()
        self.__menu.append(about_item)

        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", self.__quit_cb, None)
        quit_item.show()
        self.__menu.append(quit_item)

	self.__enabled_menu = {discover_item:True, prefs_item:True, 
			nobluez_item:False}
	self.__disabled_menu = {discover_item:False, prefs_item:False, 
			nobluez_item:True}

        # Init Icon Factory
        self.icon_theme = gtk.icon_theme_get_default()

    def __icon_popupmenu_cb(self, status_icon, button, activate_time, data):
        self.__menu.popup(None, None, gtk.status_icon_position_menu, button, 
			activate_time, status_icon)

    def __show_preferences_cb(self, widget, data=None):
        pass

    def __about_cb(self, widget, data=None):
        pass

    def __quit_cb(self, widget, data=None):
        sys.exit(0)

    def __discover_cb(self, discover_item):
	if discover_item.get_active():
            self.__wminput = WMInputLauncher(self.__wminput_retcode)
	    self.__wminput.start()
        else:
            self.__wminput.stop()

    def __wminput_retcode(self, retcode):
        if retcode:
            print "FALLLO!!!!!!!!!!!!!"
            self.__notificator.show_notification("Error while discovering Wiimote", "Can't discovering or using wiimote. Maybe uinput it's not loaded?", icon=ICON_NOTIFY)
        else:
            print "BIEEEEEEEEE"
            self.__notificator.show_notification("Wiimote desconected", "The Wiimote device was disconnected", icon=ICON_NOTIFY)

class WMInputLauncher(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.__callback = callback
        self.__pid = None

    def run(self):
        cmd = [WMINPUT_CMD]
        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        self.__pid = proc.pid
        retcode = proc.wait()
        self.__callback(retcode)

    def stop(self):
        if self.__pid:
            os.kill(self.__pid, signal.SIGINT)
            self.__pid = None

if __name__ == '__main__':
    from dbus.mainloop.glib import DBusGMainLoop
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    wiisystray = WiimoteManager()

    bus = dbus.SystemBus()
    bus.add_signal_receiver(wiisystray.enable, 
            dbus_interface="org.bluez.Manager", signal_name="AdapterAdded")
    bus.add_signal_receiver(wiisystray.disable, 
            dbus_interface="org.bluez.Manager", signal_name="AdapterRemoved")
    gobject.MainLoop().run()
