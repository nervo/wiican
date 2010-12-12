# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2010 J. Félix Ontañón
#
# Almost based on arista.inputs module:
# Copyright 2008 - 2010 Daniel G. Taylor <dan@programmer-art.org>
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

import gobject
import gudev

WIIMOTE_DEVICE_NAME = '"Nintendo Wiimote"'

class WiimoteDevice(object):
    """A simple object representing a Wiimote device."""
    
    def __init__(self, device):
        """Create a new input Wiimote device
            
        @type device: gudev.Device
        @param device: The device that we are using as wiimote
        """
        self.device = device

    @property
    def nice_label(self):
        return self.device.get_sysfs_attr('name')
    
    @property
    def path(self):
        """Get the sysfs_path for this device
            
        @rtype: string
        @return: The sysfs path
        """
        return self.device.get_sysfs_path()

class WiimoteFinder(gobject.GObject):
    """
    An object that will find and monitor Wiimote devices on your 
    machine and emit signals when are connected / disconnected
    """
    
    __gsignals__ = {
        'connected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
            (gobject.TYPE_PYOBJECT,)),
        'disconnected': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
            (gobject.TYPE_PYOBJECT,)),
    }
    
    def __init__(self):
        """
        Create a new WiimoteFinder and attach to the udev system to 
        listen for events.
        """
        self.__gobject_init__()

        self.client = gudev.Client(['input'])
        self.wiimotes = {}

        for device in self.client.query_by_subsystem('input'):
            if device.get_property('NAME') == WIIMOTE_DEVICE_NAME:
                path = device.get_sysfs_path()
                self.wiimotes[path] = WiimoteDevice(device)

        self.client.connect('uevent', self.event)

    def event(self, client, action, device):
        """Handle a udev event"""

        return {
            "add": self.device_added,
            "remove": self.device_removed,
        }.get(action, lambda x,y: None)(device)
    
    def device_added(self, device):
        """Called when a device has been added to the system"""
        
        if device.get_property('NAME') == WIIMOTE_DEVICE_NAME:
            path = device.get_sysfs_path()
            self.wiimotes[path] = WiimoteDevice(device)
            self.emit('connected', self.wiimotes[path])

    def device_removed(self, device):
        """Called when a device has been removed from the system"""
        
        if device.get_property('NAME') == WIIMOTE_DEVICE_NAME:
            path = device.get_sysfs_path()
            self.emit('disconnected', self.wiimotes[path])
            del(self.wiimotes[path])

gobject.type_register(WiimoteFinder)

if __name__ == "__main__":
    import gobject
    
    def found(finder, device):
        print device.path + ": " + device.nice_label
    
    def lost(finder, device):
        print device.path + ": " + device.nice_label
    
    finder = WiimoteFinder()
    finder.connect('connected', found)
    finder.connect('disconnected', lost)
    
    loop = gobject.MainLoop()
    loop.run()
