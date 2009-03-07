import gtk
import gobject

from gtk import glade

import defs
import dotconfig

MAPPING_GLADE = 'mapping.glade'

class WiiMappingDialog:
    def __init__(self):
        def load_widgets(xml):
            mapping_dlg = xml.get_widget('mapping_dlg')
            mapping_list = xml.get_widget('mapping_list')

            # Get buttons      
            ok_btn = xml.get_widget('ok_btn')
            new_btn = xml.get_widget('new_btn')
            edit_btn = xml.get_widget('edit_btn')
            delete_btn = xml.get_widget('delete_btn')
            up_btn = xml.get_widget('up_btn')
            down_btn = xml.get_widget('down_btn')

            # Connect buttons to methods
            ok_btn.connect('clicked', self.__close_cb, mapping_list)
            new_btn.connect('clicked', self.__new_cb, mapping_list)
            edit_btn.connect('clicked', self.__edit_cb, mapping_list)
            delete_btn.connect('clicked', self.__delete_cb, mapping_list)
            up_btn.connect('clicked', self.__up_cb, mapping_list)
            down_btn.connect('clicked', self.__down_cb, mapping_list)

            return mapping_dlg, mapping_list

        def load_model(files):
            model = gtk.ListStore(gtk.gdk.Pixbuf, # Icon
                        gobject.TYPE_STRING, # Name
                        gobject.TYPE_BOOLEAN,# Visible
                        gobject.TYPE_INT,    # Position
                        gobject.TYPE_STRING, # Description
                        gobject.TYPE_STRING, # File_path
                        gobject.TYPE_STRING) # Icon_path

            # Set the model items from files metadata and order
            positions = {}
            row_index = 0
            for file in files :
                meta = dotconfig.get_mapping_file_metadata(file)
                icon = gtk.gdk.pixbuf_new_from_file_at_size(meta['icon'], 
                        16, 16)
                model.append([icon, meta['name'], meta['visible'], 
                    meta['position'], meta['description'], file, meta['icon']])
                positions[meta['position']]=row_index # map items and positions
                row_index += 1

            model.reorder(positions.values()) # dict type applies meta order
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
            mapping_list.append_column(gtk.TreeViewColumn('Name', 
                        name_cell, text=1))

            visible_column = gtk.TreeViewColumn('Visble', visible_cell, 
                    active=2)
            mapping_list.append_column(visible_column)

            mapping_list.set_search_column(1)

        # Get the widgets
        xml = glade.XML(MAPPING_GLADE, None, None)
        self.__mapping_dlg, self.__mapping_list = load_widgets(xml)

        # Setup mapping_list
        config_files = dotconfig.DotConfig(defs.USER_CONFIG_DIR, 
            defs.CONFIG_SKEL)
        files = config_files.get_files('*.wminput')
        self.__mapping_list.set_model(load_model(files))

        # Setup the treeview
        load_treeview(self.__mapping_list)

        self.show()

    def show(self):
        self.__mapping_dlg.show()

    def __close_cb(self, widget, mapping_list):
        model = mapping_list.get_model()
        row_index = 0
        for row in model:
            dotconfig.set_mapping_file_metadata(
                    name=row[1],        # Name
                    visible=row[2],     # Visible
                    position=row_index, # Position
                    description=row[4], # Description
                    file_path=row[5],   # File_path
                    icon=row[6])        # Icon_path
            row_index += 1

        self.__mapping_dlg.destroy()

    def __new_cb(self, widget, mapping_list):
        print 'new'

    def __edit_cb(self, widget, mapping_list):
        print 'edit'
    
    def __delete_cb(self, widget, mapping_list):
        print 'delete'

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
    mapping_dlg.show()
    gobject.MainLoop().run()
