import gtk
from gtk import glade

MAPPING_GLADE = 'mapping.glade'

class WiiMappingDialog:
    def __init__(self):
        xml = glade.XML(MAPPING_GLADE, None, None)
        self.__mapping_dlg = xml.get_widget('mapping_dlg')
        self.__mapping_list = xml.get_widget('mapping_list')

        self.__mapping_list.set_model(gtk.ListStore(str))
        self.__mapping_list.append_column(gtk.TreeViewColumn('mapping',
                    gtk.CellRendererText(), text=0))
        self.__mapping_list.set_search_column(0)

        self.__close_btn = xml.get_widget('close_btn')
        self.__new_btn = xml.get_widget('new_btn')
        self.__edit_btn = xml.get_widget('edit_btn')
        self.__delete_btn = xml.get_widget('delete_btn')
        self.__up_btn = xml.get_widget('up_btn')
        self.__down_btn = xml.get_widget('down_btn')

        self.__close_btn.connect('clicked', self.__close_cb)
        self.__new_btn.connect('clicked', self.__new_cb)
        self.__edit_btn.connect('clicked', self.__edit_cb)
        self.__delete_btn.connect('clicked', self.__delete_cb)
        self.__up_btn.connect('clicked', self.__up_cb)
        self.__down_btn.connect('clicked', self.__down_cb)

        self.__mapping_dlg.show()

    def show(self):
        self.__mapping_dlg.show()

    def __close_cb(self, widget):
        self.__mapping_dlg.hide()

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
