import gtk.gdk

#TODO: Replace this with gtk.gdk.PixbufAnimation
class PngAnimation:
    def __init__(self, files=[], thumb_pixbuf=None):
        self.__frames = []
        self.__current_frame = -1
 
        for file in files:
            self.append(file, thumb_pixbuf)

    def append(self, file, thumb_pixbuf=None):
        frame = gtk.gdk.pixbuf_new_from_file(file)
        if thumb_pixbuf:
            frame = self.__composite_thumb(thumb_pixbuf, frame)

        self.__frames.append(frame)

    #TODO: Maybe a not-to-cycle arg?
    def next(self):
        self.__current_frame = (self.__current_frame + 1) % len(self.__frames)
        return self.__frames[self.__current_frame]

    def __composite_thumb(self, source, dest):
        dest = dest.add_alpha(True, chr(0xff), chr(0xff), chr(0xff))
        thumb = source.scale_simple(32, 32, gtk.gdk.INTERP_BILINEAR)
        thumb.composite(dest, 0, 0, dest.get_width(), dest.get_height(),
                dest.get_width() - thumb.get_width(),
                dest.get_height() - thumb.get_height(),
                1, 1, gtk.gdk.INTERP_BILINEAR, 255)
        return dest
