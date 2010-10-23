#!/usr/bin/python
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

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop

# The status codes
from wiican.service import WC_BLUEZ_PRESENT, WC_UINPUT_PRESENT, WC_WIIMOTE_DISCOVERING

# A callback to receive wiimote connection status changes
def status_cb(new_status):
    # Only check if wiimote it's disconnected
    if not new_status & WC_WIIMOTE_DISCOVERING:
        print 'Wiimote its disconnected'
        
if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    
    wiican_iface = dbus.Interface(bus.get_object ('org.gnome.Wiican', 
        '/org/gnome/Wiican'), 'org.gnome.Wiican')

    # Check the current wiimote connection status before trying to connect
    cur_status = wiican_iface.GetStatus()

    if not cur_status & WC_UINPUT_PRESENT:
        print 'Not uinput module present'
    elif not cur_status & WC_BLUEZ_PRESENT:
        print 'Not bluetooth adapter present'
    elif cur_status & WC_WIIMOTE_DISCOVERING:
        print 'Wiimote still in use!'
        
    # In this case we can use wiimote:
    else:
        wiican_iface.ConnectWiimote('', False)
        print 'Press 1+2 to connect wiimote'
        wiican_iface.connect_to_signal('StatusChanged', status_cb,
            dbus_interface='org.gnome.Wiican')
    
        gobject.MainLoop().run()
