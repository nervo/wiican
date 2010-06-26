# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2009, 2010 J. Félix Ontañón
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
# Authors : J. Félix Ontañón <felixonta@gmail.com>
# 
###

import sys
import os

import gtk
import gobject
import dbus

from defs import *
from notificator import Notificator
from pnganimation import PngAnimation
from mapping import MappingManagerDialog

import service
from mappingmanager import mapping_manager, Mapping, MappingManagerError

class WiimoteStatusIcon(gtk.StatusIcon):
    def __init__(self):
        super(WiimoteStatusIcon, self).__init__()
        self.set_visible(True)

        # Load UI
        builder = gtk.Builder()
        if not builder.add_from_file(WIIMOTEMANAGER_UI):
            raise 'Cant load %s' % WIIMOTEMANAGER_UI
        builder.connect_signals(self)
        
        self.aboutdlg = builder.get_object('WiiAboutDialog')
        self.main_menu = builder.get_object('main_menu')
        
        self.aboutdlg.connect('response', lambda d, r: d.hide())
        self.connect('popup-menu', self.__icon_popupmenu_cb, None)
        self.connect('activate', self.__activate_cb)

        self.__load_mappings_menu()
        self.__notificator = Notificator('wiican')
        
        # Connect to wiican service
        bus = dbus.SessionBus()  
        self.__wiican_iface = dbus.Interface(bus.get_object ('org.gnome.Wiican', 
            '/org/gnome/Wiican'), 'org.gnome.Wiican')
        self.__cur_status = self.__wiican_iface.GetStatus()
        self.__status_cb(self.__cur_status)
        self.__wiican_iface.connect_to_signal('StatusChanged', self.__status_cb, 
            dbus_interface='org.gnome.Wiican')
                        
    def __status_cb(self, new_status):
        #print 'New:', new_status, 'Old:', self.__cur_status
        if not new_status & service.WC_BLUEZ_PRESENT:
            self.__set_no_bluetooth_st()
        elif not new_status & service.WC_UINPUT_PRESENT:
            self.__set_no_uinput_st()
        elif new_status & service.WC_WIIMOTE_DISCOVERING: 
            self.__discovering_st()
        elif new_status & (service.WC_UINPUT_PRESENT | service.WC_BLUEZ_PRESENT):
            self.__idle_st()

        self.__cur_status = new_status

    def __set_no_bluetooth_st(self):
        self.set_from_file(ICON_OFF)
        self.set_tooltip(_('Plug a bluetooth adapter'))
        self.__disconnect_item.set_sensitive(False)

    def __set_no_uinput_st(self):
        self.set_from_file(ICON_OFF)
        self.set_tooltip(_('Please load uinput module first'))
        self.__disconnect_item.set_sensitive(False)

    def __idle_st(self):
        self.__disconnect_item.set_sensitive(False)
        self.set_from_file(ICON_ON)
        self.set_tooltip(_('Hold left button for use wiimote\n' \
                'Right button for menu'))

    def __discovering_st(self):
        def animate():
    	    if not self.__cur_status & service.WC_WIIMOTE_DISCOVERING:
                return False
            else:
                self.set_from_pixbuf(self.__animation.next())
                return True

        self.__disconnect_item.set_sensitive(True)
        self.set_tooltip(_('Discovering Wiimote'))
        gobject.timeout_add(500, animate)

    def __load_mappings_menu(self):
        self.__mappings_menu = gtk.Menu()

        disconnect_item = gtk.ImageMenuItem(gtk.STOCK_DISCONNECT)
        disconnect_item.connect('activate', self.__discover_cb, -1)
        disconnect_item.show()
        self.__mappings_menu.append(disconnect_item)
        self.__disconnect_item = disconnect_item

        sep_item = gtk.SeparatorMenuItem()
        sep_item.show()
        self.__mappings_menu.append(sep_item)

        mapping_manager.scan()
        for path, mapping in [item.values() for item in mapping_manager.mapping_bag.values()]:
            icon = gtk.gdk.pixbuf_new_from_file_at_size(mapping.get_icon(), 16, 16)
            menuitem = gtk.ImageMenuItem(mapping.get_name())
            menuitem.set_tooltip_text(mapping.get_comment())
            menuitem.set_image(gtk.image_new_from_pixbuf(icon))
            menuitem.connect('activate', self.__discover_cb, os.path.join(path, 'mapping.wminput'))
            menuitem.show()
            self.__mappings_menu.append(menuitem)

    def __icon_popupmenu_cb(self, status_icon, button, activate_time, data):
        self.main_menu.popup(None, None, gtk.status_icon_position_menu, button, 
			        activate_time, status_icon)

    def __activate_cb(self, status_icon):
        if self.__cur_status & (service.WC_UINPUT_PRESENT | service.WC_BLUEZ_PRESENT):
            self.__mappings_menu.popup(None, None, 
                    gtk.status_icon_position_menu, 1, 
                    gtk.get_current_event_time(), status_icon)

    def preferences_cb(self, widget):
        mapping_dlg = MappingManagerDialog()
        self.__load_mappings_menu()

    def about_cb(self, widget):
        self.aboutdlg.show()

    def quit_cb(self, widget):
        sys.exit(0)

    def __discover_cb(self, discover_item, config=None):
        print config
        if self.__cur_status & service.WC_WIIMOTE_DISCOVERING:
            self.__wiican_iface.DisconnectWiimote()
        
        if config and config != -1:
            # FIXME: This is awful
            #overlap_icon = discover_item.get_image().get_pixbuf()
            #if overlap_icon.get_pixels() == gtk.gdk.pixbuf_new_from_file_at_size(ICON_DEFAULT, 16, 16).get_pixels():
            #    overlap_icon = None
            self.__animation = PngAnimation([ICON_CONN1, ICON_CONN2, ICON_CONN3, ICON_ON])
            self.__wiican_iface.ConnectWiimote(config, False)
            self.__notificator.display_notification(title=_('Press 1+2'), 
                text=_('To put you Wiimote in discoverable mode now'),
                icon='wiican')
