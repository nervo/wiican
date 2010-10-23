# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Copyright (c) 2009 J. Félix Ontañón
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

import gtk.gdk

#TODO: Replace this with gtk.gdk.PixbufAnimation
class PngAnimation:
    def __init__(self, pixbufs=[], thumb_pixbuf=None):
        self.__frames = []
        self.__current_frame = -1
 
        for pixbuf in pixbufs:
            self.append(pixbuf, thumb_pixbuf)

    def append(self, frame, thumb_pixbuf=None):
        if thumb_pixbuf:
            frame = self.__composite_thumb(thumb_pixbuf, frame)

        self.__frames.append(frame)

    #TODO: Maybe a not-to-cycle arg?
    #TODO: Use yield for generator
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
