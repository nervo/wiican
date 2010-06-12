# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Mostly inspired from Listen's mediaplayer notify widged
#
# CommieCC is the legal property of J. Félix Ontañón <felixonta@gmail.com>
# Copyright (c) 2009 J. Félix Ontañón
# 
# Listen is the legal property of mehdi abaakouk <theli48@gmail.com>
# Copyright (c) 2006 Mehdi Abaakouk 
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###

import gtk
import gobject

NOTIF_IFACE = 'org.freedesktop.Notifications'
NOTIF_PATH = '/org/freedesktop/Notifications'

DEF_TIMEOUT = 10000
DEF_ICON = gtk.STOCK_INFO
DEF_URGENCY = 1

try:
    import dbus
    if getattr(dbus, 'version', (0,0,0)) >= (0,41,0):
        import dbus.glib
except: dbus_imported = False
else: dbus_imported=True

class Notificator(gobject.GObject):
    SIGNAL = (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                (gobject.TYPE_PYOBJECT,))
                
    __gsignals__ = {
        'action_invoked' : SIGNAL,
    }
    
    def __init__(self, app_name, desktop_entry=None):
        gobject.GObject.__init__(self)

        self.app_name = app_name
        self.desktop_entry = desktop_entry
       
        if dbus_imported:
            try: bus = dbus.SessionBus()
            except: bus = None
                
        if dbus_imported and bus:
            self.dbus_notify = dbus.Interface(bus.get_object(NOTIF_IFACE, 
                NOTIF_PATH), NOTIF_IFACE)
        else:
            self.dbus_notify = None
            
        self.dbus_notify.connect_to_signal("ActionInvoked", self.__action_cb)
            
    def display_notification(self, title, text, icon=DEF_ICON,
            urgency=DEF_URGENCY, timeout=DEF_TIMEOUT, actions=[], replaces_id=0):
        if self.dbus_notify != None:  
            hints = self.__get_hints(urgency)
            return self.dbus_notify.Notify(self.app_name, replaces_id, icon, 
                title, text, actions, hints, timeout)
        return 0

    def __action_cb(self, replaces_id, action_key):
        self.emit('action_invoked', action_key)
        
    def __get_hints(self, urgency=DEF_URGENCY):
        hints = {}
        
        if self.desktop_entry:
            hints['desktop-entry'] = self.desktop_entry
            
        hints['urgency'] = urgency

        return hints
