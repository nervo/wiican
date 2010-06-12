#!/usr/bin/python

import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from wiican import wiimotemanager

# Gen .in files with @PREFIX@ replaced
for filename in ['org.gnome.wiican.service', 'wiican/defs.py']:
    infile = open(filename + '.in', 'r')
    data = infile.read().replace('@PREFIX@', '.')
    infile.close()

    outfile = open(filename, 'w')
    outfile.write(data)
    outfile.close()

DBusGMainLoop(set_as_default=True)
wiican = wiimotemanager.WiimoteStatusIcon()
gobject.MainLoop().run()
