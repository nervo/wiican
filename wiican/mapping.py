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

import os.path

import gtk
import webbrowser

import defs
from mappingmanager import mapping_manager, Mapping, MappingManagerError

ICON_COL, NAME_COL, COMMENT_COL, VISIBLE_COL, MAPPING_ID_COL = range(5)
DEFAULT_PIXMAP_DIR = '/usr/share/pixmaps'

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
        self.set_current_folder(DEFAULT_PIXMAP_DIR)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

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
        if not builder.add_objects_from_file(defs.MAPPING_UI, 
                ['mapping_editor_dlg']):
            raise 'Cant load %s' % defs.MAPPING_UI
        builder.connect_signals(self)
        
        self.mapping_editor_dlg = builder.get_object('mapping_editor_dlg')
        self.name_entry = builder.get_object('name_entry')
        self.comment_entry = builder.get_object('comment_entry')
        self.file_buffer = builder.get_object('file_textview').get_buffer()
        self.icon_btn = builder.get_object('icon_btn')
        
        # Set initial values
        self.name_entry.set_text(self.mapping.get_name())
        self.comment_entry.set_text(self.mapping.get_comment())
        self.file_buffer.set_text(self.mapping.get_mapping())
        
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.mapping.get_icon(),
            48, 48)
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
        self.icon_btn.set_image(image)

    def set_title(self, title=''):
        self.mapping_editor_dlg.set_title(title)

    def run(self):
        return self.mapping_editor_dlg.run()

    def destroy(self):
        self.mapping_editor_dlg.destroy()

    def get_mapping(self):
        start, end = self.file_buffer.get_bounds()
        self.mapping.set_mapping(self.file_buffer.get_text(start, end))
        self.mapping.set_name(self.name_entry.get_text())
        self.mapping.set_comment(self.comment_entry.get_text())

        return self.mapping

    def link_btn_clicked_cb(self, widget):
        webbrowser.open(widget.get_uri())

    def icon_btn_clicked_cb(self, widget):
        icon_dlg = IconChooserDialog(parent=self.mapping_editor_dlg)

        if icon_dlg.run() == gtk.RESPONSE_OK:
            filename = icon_dlg.get_filename()
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 48, 48)
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            widget.set_image(image)
            self.mapping.set_icon(filename)

        icon_dlg.destroy()

class MappingManagerDialog(object):
    mapping_filter = gtk.FileFilter()
    mapping_filter.set_name(_('Wiican Mapping Package'))
    mapping_filter.add_mime_type('application/x-tar')
    mapping_filter.add_pattern('*.tgz')
    mapping_filter.add_pattern('*.tar.gz')
    
    def __init__(self):    
        builder = gtk.Builder()
        if not builder.add_objects_from_file(defs.MAPPING_UI, 
                ['mapping_manager_dlg', 'image3', 'image4', 'mapping_store']):
            raise 'Cant load %s' % defs.MAPPING_UI
        builder.connect_signals(self)
        
        self.mapping_dlg = builder.get_object('mapping_manager_dlg')
        self.mapping_store = builder.get_object('mapping_store')
        self.mapping_list = builder.get_object('mapping_list')
        
        for mapping_id, mapping in mapping_manager.items():
            icon = gtk.gdk.pixbuf_new_from_file_at_size(mapping.get_icon(), 24, 
                24)
            self.mapping_store.append([icon, mapping.get_name(), 
                mapping.get_comment(), True, mapping_id])

    def run(self):
        return self.mapping_dlg.run()

    def close_btn_clicked_cb(self, widget, data=None):
        return self.mapping_dlg.destroy()

    def new_btn_clicked_cb(self, widget):
        mapping_editor_dlg = MappingEditorDialog(Mapping())
        mapping_editor_dlg.set_title(_('Editing new mapping'))

        if mapping_editor_dlg.run() == gtk.RESPONSE_OK:
            mapping = mapping_editor_dlg.get_mapping()
            mapping_id = mapping_manager.add_new_mapping(mapping)

            icon = gtk.gdk.pixbuf_new_from_file_at_size(mapping.get_icon(), 24, 
                24)
            self.mapping_store.append([icon, mapping.get_name(), 
                mapping.get_comment(), True, mapping_id])

        mapping_editor_dlg.destroy()

    def edit_btn_clicked_cb(self, widget):
        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        
        if selected is not None:
            mapping_id = model[selected][MAPPING_ID_COL]
            mapping = mapping_manager[mapping_id]
            mapping_editor_dlg = MappingEditorDialog(mapping)
            mapping_editor_dlg.set_title(_('Editing ') + mapping.get_name())

            if mapping_editor_dlg.run() == gtk.RESPONSE_OK:
                new_mapping = mapping_editor_dlg.get_mapping()
                new_mapping.write(mapping_manager[mapping_id].get_path())
                mapping_manager[mapping_id] = new_mapping
                model[selected][ICON_COL] = \
                    gtk.gdk.pixbuf_new_from_file_at_size(new_mapping.get_icon(), 
                        24, 24)
                model[selected][NAME_COL] = new_mapping.get_name()
                model[selected][COMMENT_COL] = new_mapping.get_comment()
                
            mapping_editor_dlg.destroy()

    def mapping_list_row_activated_cb(self, widget, path, view_column):
        self.edit_btn_clicked_cb(widget)

    def delete_btn_clicked_cb(self, widget):
        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            delete_message = _('Are you sure you want to completely remove this mapping?')

            delete_dlg = gtk.MessageDialog(parent = self.mapping_dlg,
                flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                type = gtk.MESSAGE_QUESTION,
                buttons = gtk.BUTTONS_YES_NO,
                message_format = delete_message)
                
            delete_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)    
            delete_dlg.set_title(_('Deleting mappings'))
            
            if delete_dlg.run() == gtk.RESPONSE_YES:
                mapping_id = model[selected][MAPPING_ID_COL]
                del(mapping_manager[mapping_id])
                model.remove(selected)
                
            delete_dlg.destroy()

    def mapping_list_key_release_event_cb(self, widget, event):
       if event.keyval == gtk.gdk.keyval_from_name("Delete"):
            self.delete_btn_clicked_cb(None)

    def import_btn_clicked_cb(self, widget):
        import_dlg = gtk.FileChooserDialog(_('Import mapping...'), 
                self.mapping_dlg, gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, 
                gtk.RESPONSE_OK))
        import_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)                    
        import_dlg.add_filter(self.mapping_filter)
            
        if import_dlg.run() == gtk.RESPONSE_OK:
            filename = import_dlg.get_filename()
        else:
            return
        import_dlg.destroy()

        try:
            mapping_id = mapping_manager.import_mapping(filename)
        except MappingManagerError:
            error_importing_message = _('Wiican Mapping Package import failed!')
            error_importing_dlg = gtk.MessageDialog(parent = self.mapping_dlg,
                flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                type = gtk.MESSAGE_ERROR,
                buttons = gtk.BUTTONS_CLOSE,
                message_format = error_importing_message)
            error_importing_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            error_importing_dlg.run()
            error_importing_dlg.destroy()
            return
            
        mapping = mapping_manager[mapping_id]
        icon = gtk.gdk.pixbuf_new_from_file_at_size(mapping.get_icon(), 24, 24)
        self.mapping_store.append([icon, mapping.get_name(), 
            mapping.get_comment(), True, mapping_id])
        
    def export_btn_clicked_cb(self, widget):
        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            mapping_id = model[selected][MAPPING_ID_COL]
            mapping = mapping_manager[mapping_id]
            
            export_dlg = gtk.FileChooserDialog(_('Exporting mapping...'), 
                    self.mapping_dlg, gtk.FILE_CHOOSER_ACTION_SAVE,
                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, 
                    gtk.RESPONSE_OK))
            export_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            export_dlg.set_do_overwrite_confirmation(True)
            export_dlg.set_current_folder(os.path.expanduser("~/"))
            export_dlg.set_current_name(mapping.get_name())
            export_dlg.set_modal(True)
            export_dlg.add_filter(self.mapping_filter)

            if export_dlg.run() == gtk.RESPONSE_OK:
                dest_file_path = export_dlg.get_filename()
                #TODO: Check writability before export (or wait for gnome-bug #137515)
                mapping_manager.export_mapping(mapping_id, dest_file_path)
            export_dlg.destroy()
              
    def up_btn_clicked_cb(self, widget):
        # From PyGTK FAQ Entry 13.51
        # http://faq.pygtk.org/index.py?req=show&file=faq13.051.htp
        def iter_prev(iter, model):
            path = model.get_path(iter)
            position = path[-1]
            if position == 0:
                return None
            prev_path = list(path)[:-1]
            prev_path.append(position - 1)
            prev = model.get_iter(tuple(prev_path))
            return prev

        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            selected_row = model.get_path(selected)[0]
            if selected_row > 0:
                prev = iter_prev(selected, model)
                model.swap(prev, selected)
                mapping_manager.swap(model[prev][MAPPING_ID_COL], 
                    model[selected][MAPPING_ID_COL])

    def down_btn_clicked_cb(self, widget):
        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            selected_row = model.get_path(selected)[0]
            if selected_row < len(model)-1:
                next = model.iter_next(selected)
                model.swap(selected, next)
                mapping_manager.swap(model[selected][MAPPING_ID_COL], 
                    model[next][MAPPING_ID_COL])
