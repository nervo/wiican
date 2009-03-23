import sys
import os

import gtk
from gtk import glade

import pynotify
import gobject
import dbus
import subprocess
import threading
import signal

from defs import *
from dotconfig import *
from notificator import Notificator
from pnganimation import PngAnimation
from mapping import WiiMappingDialog

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

class WiimoteManager:
    def __init__(self):
        self.__icon = WiimoteStatusIcon()
        self.__bluediscover = BlueDiscover()
        self.__wiimote_udi = None

        pynotify.init("wiistray")

        self.__notificator = Notificator()
        self.__notificator.set_status_icon(self.__icon)

        adapter = self.__bluediscover.any_adapter()
        if adapter:
            self.enable(adapter)
        else:
            self.disable(adapter)

    def enable(self, device):
        self.__icon.set_state("idle")

    def disable(self, device):
        if not self.__bluediscover.any_adapter():
            self.__icon.set_state("nobluetooth")

    def plug_cb(self, udi):
        bus = dbus.SystemBus()
        device_dbus_obj = bus.get_object(HAL_URI, udi)
        properties = device_dbus_obj.GetAllProperties(dbus_interface=HAL_DEVICE_IFACE)

        try:
            if "Nintendo Wiimote" in properties["input.product"]:
                self.__wiimote_udi = udi
                print "Connected"
                self.__notificator.show_notification("Connected", 
                        "Put Wiimote in discoverable mode now (press 1+2)")
                self.__icon.set_state("discovering")
        except:
            pass

    def unplug_cb(self, udi):
        if self.__wiimote_udi == udi:
            print "Disconnected"
            self.__notificator.show_notification("Disconnected", "Wiimote off")
            self.__icon.set_state("idle")


class WiimoteStatusIcon(gtk.StatusIcon):
    def __init__(self):
        gtk.StatusIcon.__init__(self)
        self.__load_menu()
        self.__load_mappers_menu()
        self.__notificator = Notificator()
        self.__notificator.set_status_icon(self)

        #TODO: Maybe a custom gobject type makes this smarter
        self.__states = {"nobluetooth": self.__no_bluetooth_st,
            "idle": self.__idle_st,
            "discovering": self.__discovering_st,
            "discovered": self.__discovered_st}
	
        self.__current_state = "idle"
        self.__wminput = None

        about_wTree = glade.XML(ABOUT_DLG, None, None)
        self.__aboutdlg = about_wTree.get_widget('WiiAboutDialog')
        self.__aboutdlg.connect("response", lambda d, r: d.hide())
        self.connect("popup-menu", self.__icon_popupmenu_cb, None)
        self.connect("activate", self.__activate_cb)

        self.set_visible(True)

    def set_state(self, state):
        #TODO: Maybe raise exception here
        if not self.__states.has_key(state):
            return
        self.__states[state]()
        self.__current_state = state

    def __no_bluetooth_st(self):
        self.set_from_file(ICON_OFF)
        self.set_tooltip('Plug a bluetooth adapter')
        self.__disconnect_item.set_sensitive(False)

    def __idle_st(self):
        self.__disconnect_item.set_sensitive(False)
        self.set_from_file(ICON_ON)
        self.set_tooltip('Hold left button for use wiimote\nRight button for menu')

    def __discovering_st(self):
        def animate():
	    if self.__current_state != "discovering":
                return False
            else:
                self.set_from_pixbuf(self.__animation.next())
                return True

        self.__disconnect_item.set_sensitive(True)
        self.set_tooltip('Discovering Wiimote')
        gobject.timeout_add(500, animate)

    #TODO: Useless yet!
    def __discovered_st(self):
        self.__disconnect_item.show()
        self.set_from_file(ICON_ON)
        self.set_tooltip('Use your wiimote')
        self.__disconnect_item.set_sensitive(True)
      
    def __load_menu(self):
        self.__menu = gtk.Menu()

        nobluez_item = gtk.MenuItem("No bluetooth adapters")
        self.__menu.append(nobluez_item)

        prefs_item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
        prefs_item.connect("activate", self.__show_preferences_cb)
        prefs_item.show()
        self.__menu.append(prefs_item)

        sep_item = gtk.SeparatorMenuItem()
        sep_item.show()
        self.__menu.append(sep_item)

        about_item = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
        about_item.connect('activate', self.__about_cb)
        about_item.show()
        self.__menu.append(about_item)

        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", self.__quit_cb)
        quit_item.show()
        self.__menu.append(quit_item)

        # Init Icon Factory
        self.icon_theme = gtk.icon_theme_get_default()

    def __load_mappers_menu(self):
        self.__mappers_menu = gtk.Menu()
        config_files = DotConfig(USER_CONFIG_DIR, CONFIG_SKEL)

        disconnect_item = gtk.ImageMenuItem(gtk.STOCK_DISCONNECT)
        disconnect_item.connect('activate', self.__discover_cb, -1)
        disconnect_item.show()
        disconnect_item.set_sensitive(False)
        self.__mappers_menu.append(disconnect_item)
        self.__disconnect_item = disconnect_item

        sep_item = gtk.SeparatorMenuItem()
        sep_item.show()
        self.__mappers_menu.append(sep_item)

        # Add every wminput config file as menu item
        for file in config_files.get_files('*.wminput'):
            meta = read_metadata(file)
            if not meta['visible']:
                continue
            icon = gtk.gdk.pixbuf_new_from_file_at_size(meta['icon'], 16, 16)
            item = gtk.ImageMenuItem(meta['name'])
            if meta['description']:
                item.set_tooltip_text(meta['description'])
            item.set_image(gtk.image_new_from_pixbuf(icon))
            item.connect('activate', self.__discover_cb, file)
            item.show()
            self.__mappers_menu.append(item)
    
    def __icon_popupmenu_cb(self, status_icon, button, activate_time, data):
        self.__menu.popup(None, None, gtk.status_icon_position_menu, button, 
			        activate_time, status_icon)

    def __activate_cb(self, status_icon):
        if self.__current_state not in ["nobluetooth"]:
            self.__mappers_menu.popup(None, None, 
                    gtk.status_icon_position_menu, 1, gtk.get_current_event_time(), status_icon)

    def __show_preferences_cb(self, widget):
        mapping_dlg = WiiMappingDialog()
        if mapping_dlg.run() == gtk.RESPONSE_OK:
            self.__load_mappers_menu()
            mapping_dlg.destroy()

    def __about_cb(self, widget):
        self.__aboutdlg.show()

    def __quit_cb(self, widget):
        if self.__wminput:
            self.__wminput.stop()

        sys.exit(0)

    def __discover_cb(self, discover_item, config=None):
        if self.__wminput and self.__wminput.running():
            self.__wminput.stop()
        
        if config and config != -1:
            self.__animation = PngAnimation(
                    [ICON_CONN1, ICON_CONN2, ICON_CONN3, ICON_ON],
                    discover_item.get_image().get_pixbuf())
            self.__wminput = WMInputLauncher(config, self.__wminput_retcode)
            self.__wminput.start()
            
    def __wminput_retcode(self, retcode):
        if not retcode in [-15, 0]:
            print "Fail!"
            if retcode == 255:
                self.__notificator.show_notification("Error while discovering Wiimote", "Maybe uinput it's not loaded?")
            else:
                self.__notificator.show_notification("Unknown error", "Can't discover or use wiimote")
        self.set_state("idle")


class WMInputLauncher(threading.Thread):
    def __init__(self, config_file, callback):
        threading.Thread.__init__(self)
        self.__config_file = config_file
        self.__callback = callback
        self.__pid = None

    def run(self):
        cmd = WMINPUT_CMD

        if self.__config_file:
            cmd += ['-c', self.__config_file]

        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        self.__pid = proc.pid
        retcode = proc.wait()
        self.__callback(retcode)

    def stop(self):
        # FIXME: That's awful!
        if self.__pid:
            try:
                os.kill(self.__pid, signal.SIGTERM)
            except:
                pass

            self.__pid = None

    def running(self):
        if self.__pid:
            return True

        return False

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
