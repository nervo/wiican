import gtk.gdk

#TODO: Maybe complete this with magic-methods
class PixbufAnimation():
    __frames = []
    __current_frame = -1
    
    def __init__(self, files=[]):
        for file in files:
            self.append(file)

    def append(self, file):
        self.__frames.append(gtk.gdk.pixbuf_new_from_file(file))
    
    def next(self):
        self.__current_frame = (self.__current_frame + 1) % len(self.__frames)
        return self.__frames[self.__current_frame]
