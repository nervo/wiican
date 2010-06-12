# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2009 J. Félix Ontañón
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
from gtk import glade

import pynotify
import gobject
import dbus

from defs import *
from dotconfig import *
from notificator import Notificator
from pnganimation import PngAnimation
from mapping import MappingDialog

import service

class WiimoteStatusIcon(gtk.StatusIcon):
    def __init__(self):
        def load_menu():
            menu = gtk.Menu()

            nobluez_item = gtk.MenuItem(_('No bluetooth adapters'))
            menu.append(nobluez_item)

            prefs_item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
            prefs_item.connect('activate', self.__show_preferences_cb)
            prefs_item.show()
            menu.append(prefs_item)

            sep_item = gtk.SeparatorMenuItem()
            sep_item.show()
            menu.append(sep_item)

            about_item = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
            about_item.connect('activate', self.__about_cb)
            about_item.show()
            menu.append(about_item)

            quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
            quit_item.connect('activate', self.__quit_cb)
            quit_item.show()
            menu.append(quit_item)

            return menu

        gtk.StatusIcon.__init__(self)
        self.set_visible(True)
        
        self.__menu = load_menu()
        self.__load_mappings_menu()
        self.__notificator = Notificator('wiican')

        bus = dbus.SessionBus()  
        self.__wiican_iface = dbus.Interface(bus.get_object ('org.gnome.Wiican', 
            '/org/gnome/Wiican'), 'org.gnome.Wiican')
        self.__cur_status = self.__wiican_iface.GetStatus()

        if not self.__cur_status & service.WC_BLUEZ_PRESENT:
            self.__set_no_bluetooth_st()
        elif not self.__cur_status & service.WC_UINPUT_PRESENT:
            self.__set_no_uinput_st()
        elif self.__cur_status & (service.WC_UINPUT_PRESENT | service.WC_BLUEZ_PRESENT):
            self.__idle_st()

        self.__wiican_iface.connect_to_signal('StatusChanged', self.__status_cb, 
            dbus_interface='org.gnome.Wiican')
                        
        # Load about dialog
        about_builder = gtk.Builder()
        if not about_builder.add_from_file(ABOUT_DLG):
            raise 'Cant load %s' % ABOUT_DLG

        self.__aboutdlg = about_builder.get_object('WiiAboutDialog')
        self.__aboutdlg.connect('response', lambda d, r: d.hide())

        # Connect left and right click
        self.connect('popup-menu', self.__icon_popupmenu_cb, None)
        self.connect('activate', self.__activate_cb)

    def __status_cb(self, new_status):
        print 'current:', self.__cur_status, 'new:', new_status

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

    def __load_mappings_menu(self, ):
        self.__mappings_menu = gtk.Menu()
        config_files = DotConfig(USER_CONFIG_DIR, CONFIG_SKEL)

        disconnect_item = gtk.ImageMenuItem(gtk.STOCK_DISCONNECT)
        disconnect_item.connect('activate', self.__discover_cb, -1)
        disconnect_item.show()
        self.__mappings_menu.append(disconnect_item)
        self.__disconnect_item = disconnect_item

        sep_item = gtk.SeparatorMenuItem()
        sep_item.show()
        self.__mappings_menu.append(sep_item)

        # Add every wminput config file as menu item
        mapping_order = {}
        for file in config_files.get_files('*.wminput', True):
            meta = MAPPING_DEFAULT_VALUES.copy()
            meta.update(read_metadata(file))

            if not meta['visible']:
                continue

            icon = gtk.gdk.pixbuf_new_from_file_at_size(meta['icon'], 16, 16)
            item = gtk.ImageMenuItem(meta['name'])
            item.set_tooltip_text(meta['description'])
            item.set_image(gtk.image_new_from_pixbuf(icon))
            item.connect('activate', self.__discover_cb, file)
            item.show()

            # Calculate the order of mappings
            while mapping_order.has_key(meta['position']):
                meta['position'] += 1
            mapping_order[meta['position']] = item

        # python dict applies meta order
        for item in mapping_order.values():
            self.__mappings_menu.append(item)

    def __icon_popupmenu_cb(self, status_icon, button, activate_time, data):
        self.__menu.popup(None, None, gtk.status_icon_position_menu, button, 
			        activate_time, status_icon)

    def __activate_cb(self, status_icon):
        if self.__cur_status & (service.WC_UINPUT_PRESENT | service.WC_BLUEZ_PRESENT):
            self.__mappings_menu.popup(None, None, 
                    gtk.status_icon_position_menu, 1, 
                    gtk.get_current_event_time(), status_icon)

    def __show_preferences_cb(self, widget):
        mapping_dlg = MappingDialog()
        if mapping_dlg.run() == gtk.RESPONSE_OK:
            self.__load_mappings_menu()
        mapping_dlg.destroy()

    def __about_cb(self, widget):
        self.__aboutdlg.show()

    def __quit_cb(self, widget):
        self.__wiican_iface.Quit()
        sys.exit(0)

    def __discover_cb(self, discover_item, config=None):
        if self.__cur_status & service.WC_WIIMOTE_DISCOVERING:
            self.__wiican_iface.DisconnectWiimote()
        
        if config and config != -1:
            # FIXME: This way of compare pixbufs it's awful
            overlap_icon = discover_item.get_image().get_pixbuf()
            if overlap_icon.get_pixels() == gtk.gdk.pixbuf_new_from_file_at_size(ICON_DEFAULT, 16, 16).get_pixels():
                overlap_icon = None
            self.__animation = PngAnimation(
                    [ICON_CONN1, ICON_CONN2, ICON_CONN3, ICON_ON],
                    overlap_icon)
            self.__wiican_iface.ConnectWiimote(config, False)
            self.__notificator.display_notification(title=_('Press 1+2'), 
                text=_('To put you Wiimote in discoverable mode now'),
                icon='wiican')
