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
import webbrowser

from wiican.defs import *
from wiican.mapping import Mapping

class IconChooserDialog(gtk.FileChooserDialog):
    def __init__(self, parent, title=_('Select image icon..'), icon_size=64):

        # Do the icon preview
        def update_preview_cb(file_chooser, preview, icon_size):
            filename = file_chooser.get_preview_filename()
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 
                        icon_size, icon_size)
                preview.set_from_pixbuf(pixbuf)
                have_preview = True
            except:
                have_preview = False
            file_chooser.set_preview_widget_active(have_preview)
            return

        gtk.FileChooserDialog.__init__(self, title, parent,
                                gtk.FILE_CHOOSER_ACTION_OPEN,
                                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        self.set_default_response(gtk.RESPONSE_OK)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.add_shortcut_folder(ARTWORK_DIR)

        #TODO: Maybe a better filter it's requiered
        filter = gtk.FileFilter()
        filter.set_name(_('Images'))
        filter.add_mime_type('image/png')
        filter.add_mime_type('image/jpeg')
        filter.add_mime_type('image/gif')
        filter.add_mime_type('image/svg')        
        filter.add_pattern('*.png')
        filter.add_pattern('*.jpg')
        filter.add_pattern('*.gif')
        filter.add_pattern('*.svg')        
        self.add_filter(filter)

        # Set a preview widget 
        preview = gtk.Image()
        self.set_preview_widget(preview)
        self.connect('update-preview', update_preview_cb, preview, icon_size)

class MappingEditorDialog(object):
    def __init__(self, mapping):
        self.mapping = mapping
                    
        builder = gtk.Builder()
        if not builder.add_objects_from_file(MAPPING_UI, 
                ['mapping_editor_dlg', 'mapping_buffer']):
            raise 'Cant load %s' % MAPPING_UI
        builder.connect_signals(self)
        
        self.mapping_editor_dlg = builder.get_object('mapping_editor_dlg')
        self.name_entry = builder.get_object('name_entry')
        self.comment_entry = builder.get_object('comment_entry')
        self.version_entry = builder.get_object('version_entry')
        self.authors_entry = builder.get_object('authors_entry')
        self.mapping_buffer = builder.get_object('mapping_buffer')
        self.icon_image = builder.get_object('icon_image')
        
        #FIXME: iconfilechooser with default dialog from glade 3.6.7 crashes
        self.iconfilechooser_btn = gtk.FileChooserButton(IconChooserDialog(self.mapping_editor_dlg))
        self.iconfilechooser_btn.show()
        self.iconfilechooser_btn.connect('file-set', self.iconfilechooser_btn_file_set_cb)
        builder.get_object('hbox2').add(self.iconfilechooser_btn)

        # Populate dialog with mapping values
        self.name_entry.set_text(self.mapping.get_name() or '')
        self.comment_entry.set_text(self.mapping.get_comment() or '')
        self.version_entry.set_text(self.mapping.get_version() or '')
        self.authors_entry.set_text(self.mapping.get_authors() or '')
        self.mapping_buffer.set_text(self.mapping.get_mapping() or '')

        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.mapping.get_icon(),
            48, 48)
        self.icon_image.set_from_pixbuf(pixbuf)

    def set_title(self, title=''):
        self.mapping_editor_dlg.set_title(title)

    def run(self):
        return self.mapping_editor_dlg.run()

    def destroy(self):
        self.mapping_editor_dlg.destroy()

    def get_mapping(self):
        start, end = self.mapping_buffer.get_bounds()
        self.mapping.set_mapping(self.mapping_buffer.get_text(start, end))
        self.mapping.set_name(self.name_entry.get_text())
        self.mapping.set_comment(self.comment_entry.get_text())
        self.mapping.set_version(self.version_entry.get_text())
        self.mapping.set_authors(self.authors_entry.get_text())

        return self.mapping

    def link_btn_clicked_cb(self, widget):
        webbrowser.open(widget.get_uri())

    def iconfilechooser_btn_file_set_cb(self, widget):
        filename = self.iconfilechooser_btn.get_filename()
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 48, 48)
        self.icon_image.set_from_pixbuf(pixbuf)
        self.mapping.set_icon(filename)
