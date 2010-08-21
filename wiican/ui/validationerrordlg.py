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
# Authors : J. Félix Ontañón <felixonta@gmail.com>
# 
###

import gtk

from wiican.defs import WIIMOTEMANAGER_UI

class ValidationErrorDialog(object):
    error_icon = gtk.STOCK_DIALOG_ERROR

    def __init__(self, icon_file, parent=None, open_editor=False):
        builder = gtk.Builder()
        if not builder.add_objects_from_file(WIIMOTEMANAGER_UI, 
                ['ValidationErrorDialog', 'image1']):
            raise 'Cant load %s' % WIIMOTEMANAGER_UI

        self.validation_error_dlg = builder.get_object('ValidationErrorDialog')
        self.icon_image = builder.get_object('icon_image')
        self.open_editor_btn = builder.get_object('open_editor_btn')

        self.validation_error_dlg.connect('response', lambda d, r: d.hide())

        icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_file, 64, 64)        
        self.icon_image.set_from_pixbuf(self.__composite_thumb(icon))

        if parent:
            self.validation_error_dlg.set_parent(parent)
            self.validation_error_dlg.set_transient_for(parent)
            self.validation_error_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        if open_editor:
            self.open_editor_btn.show()
            self.validation_error_dlg.set_decorated(False)

    def run(self):
        return self.validation_error_dlg.run()

    def destroy(self):
        self.validation_error_dlg.destroy()

    def move(self, x, y):
        self.validation_error_dlg.move(x, y)

    def __composite_thumb(self, icon):
        error = gtk.Invisible().render_icon(self.error_icon, gtk.ICON_SIZE_BUTTON)
        thumb = error.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
        thumb.composite(icon, 0, 0, icon.get_width(), icon.get_height(),
                icon.get_width() - thumb.get_width(),
                icon.get_height() - thumb.get_height(),
                1, 1, gtk.gdk.INTERP_BILINEAR, 255)
                
        return icon
