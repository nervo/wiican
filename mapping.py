import gtk
from gtk import glade
from dotconfig import *
from defs import *

MAPPING_GLADE = 'mapping.glade'

class WiiMappingDialog:
    def __init__(self):
        self.__load_dialog()
        self.__config_files = DotConfig(USER_CONFIG_DIR, CONFIG_SKEL)

        # Populate treeview
        model = self.__mapping_list.get_model()

        for file in self.__config_files.get_files('*.wminput'):
            meta = get_mapping_file_metadata(file)
            icon = gtk.gdk.pixbuf_new_from_file_at_size(meta['icon'], 16, 16)
            model.append([icon, meta['name'].capitalize(), 
                    meta['description'], file])
            
        self.__mapping_list.set_model(model)

        self.show()

    def show(self):
        self.__mapping_dlg.show()

    def __load_dialog(self):
        xml = glade.XML(MAPPING_GLADE, None, None)
        self.__mapping_dlg = xml.get_widget('mapping_dlg')
        self.__mapping_list = xml.get_widget('mapping_list')

        # Set the treeview widget
        icon_cell = gtk.CellRendererPixbuf()
        name_cell = gtk.CellRendererText()
        name_cell.set_property('editable', True)

        list = gtk.ListStore(gtk.gdk.Pixbuf, # Icon
                            str, # Name
                            str, # Description
                            str) # File_path

        self.__mapping_list.set_model(list)
        self.__mapping_list.append_column(gtk.TreeViewColumn('icon', 
                    icon_cell, pixbuf=0))
        self.__mapping_list.append_column(gtk.TreeViewColumn('name', 
                    name_cell, text=1))
        self.__mapping_list.set_search_column(1)

        # Get buttons      
        self.__close_btn = xml.get_widget('close_btn')
        self.__new_btn = xml.get_widget('new_btn')
        self.__edit_btn = xml.get_widget('edit_btn')
        self.__delete_btn = xml.get_widget('delete_btn')
        self.__up_btn = xml.get_widget('up_btn')
        self.__down_btn = xml.get_widget('down_btn')

        # Connect buttons to methods
        self.__close_btn.connect('clicked', self.__close_cb)
        self.__new_btn.connect('clicked', self.__new_cb)
        self.__edit_btn.connect('clicked', self.__edit_cb)
        self.__delete_btn.connect('clicked', self.__delete_cb)
        self.__up_btn.connect('clicked', self.__up_cb)
        self.__down_btn.connect('clicked', self.__down_cb)

    def __close_cb(self, widget):
        self.__mapping_dlg.destroy()

    def __new_cb(self, widget):
        print 'new'
        pass

    def __edit_cb(self, widget):
        print 'edit'
        pass
    
    def __delete_cb(self, widget):
        print 'delete'
        pass

    def __up_cb(self, widget):
        print 'up'
        pass

    def __down_cb(self, widget):
        print 'down'
        pass

if __name__ == '__main__':
    import gobject

    mapping_dlg = WiiMappingDialog()
    mapping_dlg.show()
    gobject.MainLoop().run()
