# -*- coding: utf-8 -*-
# vim: ts=4
###
#
# Copyright (c) 2009-2011 J. Félix Ontañón
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

import os.path
import gtk

from wiican.defs import *
from wiican.mapping import Mapping, MappingManager, MappingManagerError
from wiican.ui.editordlg import MappingEditorDialog
from wiican.ui import UIPrefStore

ICON_COL, NAME_COL, COMMENT_COL, VISIBLE_COL, MAPPING_ID_COL = range(5)

mapping_manager = MappingManager()
pref_store = UIPrefStore()

class MappingManagerDialog(object):
    mapping_filter = gtk.FileFilter()
    mapping_filter.set_name(_('Wiican Mapping Package'))
    mapping_filter.add_mime_type('application/x-wii')
    mapping_filter.add_pattern('*.wii')

    def __init__(self):
        builder = gtk.Builder()
        if not builder.add_objects_from_file(MAPPING_UI, 
                ['mapping_manager_dlg', 'image3', 'image4', 'mapping_store',
                    'new_action', 'edit_action', 'delete_action', 
                    'import_action', 'export_action']):
            raise 'Cant load %s' % MAPPING_UI
        builder.connect_signals(self)

        self.mapping_dlg = builder.get_object('mapping_manager_dlg')
        self.mapping_store = builder.get_object('mapping_store')
        self.mapping_list = builder.get_object('mapping_list')

        # Enable Drag&Drop
        target_entries = [('catalog', gtk.TARGET_SAME_WIDGET, 0)]
        self.mapping_list.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                target_entries, gtk.gdk.ACTION_MOVE)
        self.mapping_list.enable_model_drag_dest(target_entries, 
                gtk.gdk.ACTION_MOVE)

        for mapping_id, mapping in mapping_manager.items():
            # Prevent for loading a not found icon path
            icon_path = mapping.get_icon()
            if not os.path.exists(icon_path): icon_path = ICON_DEFAULT
            
            icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_path, 24, 24)
            visible = mapping_manager.is_visible(mapping_id)
            
            mapping_name = '<b>%s</b>\n<i>%s</i>' % (mapping.get_name(), 
                mapping.get_comment())
            self.mapping_store.append([icon, mapping_name, 
                mapping.get_comment(), visible, mapping_id])

        def catch_window_size(widget, allocate):
            pref_store.options['mapping_dlg_width'] = allocate.width
            pref_store.options['mapping_dlg_height'] = allocate.height

        self.mapping_dlg.connect('size_allocate', catch_window_size)

        pref_store.loadconf()
        self.mapping_dlg.resize(pref_store.options['mapping_dlg_width'], 
            pref_store.options['mapping_dlg_height'])

    def run(self):
        runcode = self.mapping_dlg.run()
        pref_store.saveconf()
        return runcode

    def close_btn_clicked_cb(self, widget, data=None):
        pref_store.saveconf()
        return self.mapping_dlg.destroy()

    def new_action_activate_cb(self, widget):
        mapping_editor_dlg = MappingEditorDialog(Mapping())
        mapping_editor_dlg.set_title(_('Editing new mapping'))

        if mapping_editor_dlg.run() == gtk.RESPONSE_OK:
            mapping = mapping_editor_dlg.get_mapping()
            mapping_id = mapping_manager.add_new_mapping(mapping)

            icon = gtk.gdk.pixbuf_new_from_file_at_size(mapping.get_icon(), 24, 
                24)

            mapping_name = '<b>%s</b>\n<i>%s</i>' % (mapping.get_name(), 
                    mapping.get_comment())
            self.mapping_store.append([icon, mapping_name,
                mapping.get_comment(), True, mapping_id])

        mapping_editor_dlg.destroy()

    def edit_action_activate_cb(self, widget):
        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        
        if selected is not None:
            mapping_id = model[selected][MAPPING_ID_COL]
            mapping = mapping_manager[mapping_id]
            system_mapping = mapping_manager.is_system_mapping(mapping_id)
            mapping_editor_dlg = MappingEditorDialog(mapping, system_mapping)

            if mapping_editor_dlg.run() == gtk.RESPONSE_OK:
                new_mapping = mapping_editor_dlg.get_mapping()
                new_mapping_id = mapping_manager.write_mapping(new_mapping)

                if system_mapping:
                    icon = gtk.gdk.pixbuf_new_from_file_at_size(new_mapping.get_icon(), 
                        24, 24)

                    mapping_name = '<b>%s</b>\n<i>%s</i>' % (mapping.get_name(), 
                            mapping.get_comment())
                    self.mapping_store.append([icon, mapping_name,
                        mapping.get_comment(), True, mapping_id])
                else:
                    mapping_manager[mapping_id] = new_mapping
                    model[selected][ICON_COL] = gtk.gdk.pixbuf_new_from_file_at_size(new_mapping.get_icon(), 
                        24, 24)
                    model[selected][NAME_COL] = '<b>%s</b>\n<i>%s</i>' % (new_mapping.get_name(), 
                            new_mapping.get_comment())
                    model[selected][COMMENT_COL] = new_mapping.get_comment()

            mapping_editor_dlg.destroy()

    def mapping_list_row_activated_cb(self, widget, path, view_column):
        self.edit_action_activate_cb(widget)

    def delete_action_activate_cb(self, widget):
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
                try:
                    del(mapping_manager[mapping_id])
                except MappingManagerError, e:
                    delete_dlg.destroy()
                    error_importing_dlg = gtk.MessageDialog(parent = self.mapping_dlg,
                    flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    type = gtk.MESSAGE_ERROR,
                    buttons = gtk.BUTTONS_CLOSE,
                    message_format = e.message)
                    error_importing_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                    error_importing_dlg.run()
                    error_importing_dlg.destroy()
                    delete_dlg.destroy()
                    return

                model.remove(selected)
            delete_dlg.destroy()

    def mapping_list_key_release_event_cb(self, widget, event):
       if event.keyval == gtk.gdk.keyval_from_name("Delete"):
            self.delete_action_activate_cb(None)

    def import_action_activate_cb(self, widget):
        import_dlg = gtk.FileChooserDialog(_('Import mapping...'), 
                self.mapping_dlg, gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, 
                gtk.RESPONSE_OK))
        import_dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        import_dlg.add_filter(self.mapping_filter)
        import_dlg.add_shortcut_folder(MAPPING_PACKAGES_BASE_DIR)
        import_dlg.set_current_folder(pref_store.options['import_dir'])
            
        if not import_dlg.run() == gtk.RESPONSE_OK:
            import_dlg.destroy()
            return
            
        filename = import_dlg.get_filename()
        
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
            import_dlg.destroy()
            return
            
        mapping = mapping_manager[mapping_id]
        icon = gtk.gdk.pixbuf_new_from_file_at_size(mapping.get_icon(), 24, 24)

        mapping_name = '<b>%s</b>\n<i>%s</i>' % (mapping.get_name(), 
                mapping.get_comment())
        self.mapping_store.append([icon, mapping_name,
            mapping.get_comment(), True, mapping_id])

        pref_store.options['import_dir'] = import_dlg.get_current_folder()
        import_dlg.destroy()
        
    def export_action_activate_cb(self, widget):
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
            export_dlg.set_current_folder(pref_store.options['export_dir'])
            export_dlg.set_current_name(mapping.get_name()+'.wii')
            export_dlg.set_modal(True)
            export_dlg.add_filter(self.mapping_filter)

            if export_dlg.run() == gtk.RESPONSE_OK:
                dest_file_path = export_dlg.get_filename()
                if not dest_file_path.endswith('.wii'):
                    dest_file_path += '.wii'
                #TODO: Check writability before export (or wait for gnome-bug #137515)
                mapping_manager.export_mapping(mapping_id, dest_file_path)
                pref_store.options['export_dir'] = export_dlg.get_current_folder()
            export_dlg.destroy()

    def visible_cell_toggled_cb(self, widget, path):
        mapping_id = self.mapping_store[path][MAPPING_ID_COL]
        mapping_manager.set_visible(mapping_id, not self.mapping_store[path][VISIBLE_COL])
        self.mapping_store[path][VISIBLE_COL] = not self.mapping_store[path][VISIBLE_COL]
              
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
                mapping_manager.swap_mapping_order(model[prev][MAPPING_ID_COL], 
                    model[selected][MAPPING_ID_COL])

    def down_btn_clicked_cb(self, widget):
        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            selected_row = model.get_path(selected)[0]
            if selected_row < len(model)-1:
                next = model.iter_next(selected)
                model.swap(selected, next)
                mapping_manager.swap_mapping_order(model[selected][MAPPING_ID_COL], 
                    model[next][MAPPING_ID_COL])

    def mapping_list_drag_data_received_cb(self, treeview, context, x, y,
            selection, info, etime):

        selection = self.mapping_list.get_selection()
        model, selected = selection.get_selected()
        data = [model[selected][ICON_COL], model[selected][NAME_COL], \
            model[selected][COMMENT_COL], model[selected][VISIBLE_COL], \
            model[selected][MAPPING_ID_COL]]

        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)
            if position in (gtk.TREE_VIEW_DROP_BEFORE, 
                    gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                model.insert_before(iter, data)
                mapping_manager.swap_mapping_order(model[iter][MAPPING_ID_COL],
                        model[selected][MAPPING_ID_COL])
            else:
                model.insert_after(iter, data)
                mapping_manager.swap_mapping_order(model[iter][MAPPING_ID_COL],
                        model[selected][MAPPING_ID_COL], True)
        else:
            model.append(data)
            mapping_manager.swap_mapping_order(
                mapping_manager.options['mapping_sort'][-1],
                model[selected][MAPPING_ID_COL], True)

        if context.action == gtk.gdk.ACTION_MOVE:
            context.finish(True, True, etime)
        return
