import gtk
import gobject
import webbrowser

from gtk import glade

import defs
import dotconfig

class IconChooserDialog(gtk.FileChooserDialog):
    def __init__(self, parent, title="Select image icon..", icon_size=64):

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

        #TODO: Maybe a better filter it's requiered
        filter = gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.gif")
        self.add_filter(filter)

        # Set a preview widget 
        preview = gtk.Image()
        self.set_preview_widget(preview)
        self.connect("update-preview", update_preview_cb, preview, icon_size)

class EntryDialog:
    def __init__(self, name='', description='', mapping='', 
            icon_path=defs.ICON_DEFAULT):
        wTree = glade.XML(defs.ENTRY_GLADE, None, None)
        self.__entry_dlg = wTree.get_widget('entry_dlg')
        self.__name_entry = wTree.get_widget('name_entry')
        self.__desc_entry = wTree.get_widget('desc_entry')
        self.__file_buffer = wTree.get_widget('file_textview').get_buffer()
        self.__icon_path = icon_path

        # Get buttons
        icon_btn = wTree.get_widget('icon_btn')
        icon_btn.connect('clicked', self.__icon_cb)
        link_btn = wTree.get_widget('link_btn')
        link_btn.connect('clicked', self.__link_cb)

        # Set initial values
        self.__name_entry.set_text(name)
        self.__desc_entry.set_text(description)
        self.__file_buffer.set_text(mapping)
        if self.__icon_path:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(icon_path, 48, 48)
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            icon_btn.set_image(image)

    #FIXME: What a lot of proxies. I wonder if i can subclass ...
    def set_title(self, title=''):
        self.__entry_dlg.set_title(title)

    def run(self):
        return self.__entry_dlg.run()

    def destroy(self):
        self.__entry_dlg.destroy()

    def get_values(self):
        start, end = self.__file_buffer.get_bounds()

        return self.__name_entry.get_text(), \
                self.__desc_entry.get_text(), \
                self.__file_buffer.get_text(start, end), \
                self.__icon_path

    def __link_cb(self, widget):
        webbrowser.open(widget.get_uri())

    def __icon_cb(self, widget):
        icon_dlg = IconChooserDialog(parent=self.__entry_dlg)

        if icon_dlg.run() == gtk.RESPONSE_OK:
            filename = icon_dlg.get_filename()
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 48, 48)
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            widget.set_image(image)
            self.__icon_path = filename

        icon_dlg.destroy()

class WiiMappingDialog:
    def __init__(self):
        def load_widgets(wTree):
            mapping_dlg = wTree.get_widget('mapping_dlg')
            mapping_list = wTree.get_widget('mapping_list')

            # Get buttons      
            save_btn = wTree.get_widget('save_btn')
            new_btn = wTree.get_widget('new_btn')
            edit_btn = wTree.get_widget('edit_btn')
            delete_btn = wTree.get_widget('delete_btn')
            up_btn = wTree.get_widget('up_btn')
            down_btn = wTree.get_widget('down_btn')

            # Connect buttons to methods
            save_btn.connect('clicked', self.__save_cb, mapping_list)
            new_btn.connect('clicked', self.__new_cb, mapping_list)
            edit_btn.connect('clicked', self.__edit_cb, mapping_list)
            delete_btn.connect('clicked', self.__delete_cb, mapping_list)
            up_btn.connect('clicked', self.__up_cb, mapping_list)
            down_btn.connect('clicked', self.__down_cb, mapping_list)
            mapping_list.connect('row-activated', self.__row_cb)

            return mapping_dlg, mapping_list

        def load_model(files):
            model = gtk.ListStore(gtk.gdk.Pixbuf, # Icon
                        gobject.TYPE_STRING, # Name
                        gobject.TYPE_BOOLEAN,# Visible
                        gobject.TYPE_INT,    # Position
                        gobject.TYPE_STRING, # Description
                        gobject.TYPE_STRING, # File_path
                        gobject.TYPE_STRING, # Icon_path
                        gobject.TYPE_STRING) # Mapping

            # Set the model items from files metadata and order
            positions = {}
            row_index = 0

            for file in files:
                meta = defs.MAPPING_DEFAULT_VALUES.copy()
                meta.update(dotconfig.read_metadata(file))
                mapping = dotconfig.read_mapping(file)
                icon = gtk.gdk.pixbuf_new_from_file_at_size(meta['icon'], 
                        16, 16)
                while positions.has_key(meta['position']):
                    meta['position'] += 1
                model.append([icon, meta['name'], meta['visible'], 
                    meta['position'], meta['description'], file, meta['icon'],
                    mapping])
                
                positions[meta['position']]=row_index # map items and positions
                row_index += 1

            if positions:
                # python dict applies meta order
                model.reorder(positions.values())
            
            return model

        def load_treeview(mapping_list):
            # Set the cells
            icon_cell = gtk.CellRendererPixbuf()
            name_cell = gtk.CellRendererText()

            def visible_toggled_cb(cell, path, model):
                model[path][2] = not model[path][2]

            visible_cell = gtk.CellRendererToggle()
            visible_cell.connect('toggled', visible_toggled_cb, 
                    mapping_list.get_model())

            # Set the columns
            mapping_list.append_column(gtk.TreeViewColumn('', 
                        icon_cell, pixbuf=0))

            name_column = gtk.TreeViewColumn('Name', name_cell, text=1)
            name_column.set_expand(True)
            mapping_list.append_column(name_column)

            visible_column = gtk.TreeViewColumn('Visible', visible_cell, 
                    active=2)
            mapping_list.append_column(visible_column)

            mapping_list.set_search_column(1)

        # Get the widgets
        wTree = glade.XML(defs.MAPPING_GLADE, None, None)
        self.__mapping_dlg, self.__mapping_list = load_widgets(wTree)

        # Setup mapping_list
        self.__config_files = dotconfig.DotConfig(defs.USER_CONFIG_DIR, 
            defs.CONFIG_SKEL)
        files = self.__config_files.get_files('*.wminput')
        self.__mapping_list.set_model(load_model(files))

        # Mappings marked for delete
        self.__deleted = {}

        # Setup the treeview
        load_treeview(self.__mapping_list)

    def run(self):
        return self.__mapping_dlg.run()

    def destroy(self):
        return self.__mapping_dlg.destroy()

    def __save_cb(self, widget, mapping_list):
        model = mapping_list.get_model()
        row_index = 0

        # If any mapping was marked for delete, now it's time to remove files
        if self.__deleted:
            delete_message = 'Are you sure you want to completely remove ' \
                    'this mappings?:\n\n' + '\n'.join(self.__deleted.keys())

            delete_dlg = gtk.MessageDialog(parent = self.__mapping_dlg, 
                    flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                    type = gtk.MESSAGE_QUESTION,
                    buttons = gtk.BUTTONS_YES_NO,
                    message_format = delete_message)
            delete_dlg.set_title('Deleting mappings')

            if delete_dlg.run() == gtk.RESPONSE_YES:
                for file_path in self.__deleted.values():
                    # TODO: try-except block it's required
                    dotconfig.remove_mapping(file_path)

            delete_dlg.destroy()
            self.__deleted = {}

        # Make the changes effective by writing on wminput config files
        # TODO: A best approx. it's to save only the changes
        for row in model:
            if not row[5]:
                row[5] = self.__config_files.new_filename(row[1] + '_', 
                        '.wminput')
            dotconfig.write_mapping(
                    name=row[1],        # Name
                    visible=row[2],     # Visible
                    position=row_index, # Position
                    description=row[4], # Description
                    file_path=row[5],   # File_path
                    icon=row[6],        # Icon_path
                    mapping=row[7])     # Mapping
            row_index += 1

    def __new_cb(self, widget, mapping_list):
        entry_dlg = EntryDialog()
        if entry_dlg.run() == gtk.RESPONSE_OK:
            name, desc, mapping, icon_path = entry_dlg.get_values()
            icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_path, 16, 16)
            model = mapping_list.get_model()
            model.append([icon, name, True, 0, desc, None, icon_path, mapping])

        entry_dlg.destroy()

    def __edit_cb(self, widget, mapping_list):
        selection = mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            row_data = model[selected]

            entry_dlg = EntryDialog(
                    name = row_data[1],
                    description = row_data[4],
                    mapping = row_data[7],
                    icon_path = row_data[6])

            entry_dlg.set_title("Editing %s" % row_data[1])

            if entry_dlg.run() == gtk.RESPONSE_OK:
                name, desc, mapping, icon_path = entry_dlg.get_values()
                icon = gtk.gdk.pixbuf_new_from_file_at_size(icon_path, 16, 16)
                row_data[0], row_data[1] = icon, name
                row_data[4], row_data[6] = desc, icon_path
                row_data[7] = mapping
                
            entry_dlg.destroy()

    def __row_cb(self, widget, path, view_column):
        self.__edit_cb(None, widget)

    def __delete_cb(self, widget, mapping_list):
        selection = mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            row = model[selected]
            self.__deleted[row[1]] = row[5]
            model.remove(selected)

    def __up_cb(self, widget, mapping_list):
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

        selection = mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            selected_row = model.get_path(selected)[0]
            if selected_row > 0:
                prev = iter_prev(selected, model)
                model.swap(prev, selected)

    def __down_cb(self, widget, mapping_list):
        selection = mapping_list.get_selection()
        model, selected = selection.get_selected()
        if selected is not None:
            selected_row = model.get_path(selected)[0]
            if selected_row < len(model)-1:
                next = model.iter_next(selected)
                model.swap(selected, next)

if __name__ == '__main__':
    import gobject

    mapping_dlg = WiiMappingDialog()
    mapping_dlg.run()
    mapping_dlg.destroy()
    gobject.MainLoop().run()
