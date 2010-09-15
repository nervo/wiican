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

import os.path
import shutil
import exceptions

from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath

from wiican.defs import ICON_DEFAULT

class Mapping(object):
    """
    An object representation of a wiican mapping.

    A wiican mapping must be located in a single directory containing a file 
    with the wminput code, a file containing the metadata (name, description, 
    author, version) and an optional icon file.
    """
    
    # Mandatory filename for the metadata file
    info_filename = 'info.desktop'

    # Mandatory filename for the wminput config file
    mapping_filename = 'mapping.wminput'
    
    def __init__(self, path=None):
        """
        Builds a mapping object.

        Parameters:
        path -  scans the path for building a mapping object if the needed files
                where found. If None it builds an empty mapping. If some of the 
                needed files wasn't found it tries to build a mapping with the 
                found info.

        The Mapping.info_filename and Mapping.mapping_filename class attributes 
        marks the requiered filenames for the metadata file and wminput config file 
        respectively.

        The Mapping.mapping_filename file must contain wminput config file code
        The Mapping.info_filename follows XDG DesktopEntry syntax.
        
        The Mapping.info_filename contains the source of the optional associated
        icon. If no icon found or no icon directive it falls back to default 
        icon.

        There are three posibilities for icon setting:

        - An absolute path where the icon it's stored
        - Icon filename if it's stored in the same dir as Mapping.info_filename
        - Theme-icon-name for auto-getting the icon from the icon theme
        """

        self.__path = path
        
        # Getting freedesktop definition file
        self.__info = DesktopEntry()
        
        if path and os.path.exists(os.path.join(path, Mapping.info_filename)):
            self.__info.parse(os.path.join(path, Mapping.info_filename))
        else:
            self.__info.new(self.info_filename)
            self.__info.set('Type', 'Wiican Mapping')

        # Getting wminput mapping file            
        if path and os.path.exists(os.path.join(path, Mapping.mapping_filename)):
            mapping_fp = open(os.path.join(path, Mapping.mapping_filename), 'r')
            self.__mapping = mapping_fp.read()
            mapping_fp.close()
        else:
            self.__mapping = ''

        # Getting icon file path
        icon_name = self.__info.getIcon()
        if path and icon_name in os.listdir(path): # Icon included
            self.set_icon(os.path.join(path, icon_name))
        elif getIconPath(icon_name): # Theme icon
            self.set_icon(getIconPath(icon_name))
        else: # Default icon
            self.set_icon(ICON_DEFAULT)
            
    def get_path(self):
        """Returns the absolute path where the wiican mapping it's saved.
        It returns None if the mapping it's not saved yet"""

        return self.__path

    def get_name(self):
        """Gets the name of the mapping"""

        return self.__info.getName()
        
    def set_name(self, name):
        """Sets the name for the mapping"""

        self.__info.set('Name', name)
        self.__info.set('Name', name, locale=True)

    def get_comment(self):
        """Gets the descriptional comment"""

        return self.__info.getComment()

    def set_comment(self, comment):
        """Sets the descriptional comment for the mapping"""

        self.__info.set('Comment', comment)
        self.__info.set('Comment', comment, locale=True)

    def get_icon(self):
        """
        Gets the associated icon. 
        If no icon found or no icon directive it falls back to default icon.
        """

        icon_name = self.__info.getIcon()
        # Icon included
        if self.__path and icon_name in os.listdir(self.__path):
            return os.path.join(self.__path, icon_name)
        # Theme icon
        elif getIconPath(icon_name): 
            return getIconPath(icon_name)
        # Default icon
        else:
            return ICON_DEFAULT
                            
    def set_icon(self, icon_path):
        """
        Sets the icon for the mapping. There are three posibilities for icon 
        setting:

        - An absolute path where the icon it's stored
        - Icon filename if it's stored in the same dir as Mapping.info_filename
        - Theme-icon-name for auto-getting the icon from the icon theme        
        """

        self.__info.set('Icon', icon_path)

    def get_authors(self):
        """Gets the mapping author/s"""

        return self.__info.get('X-Authors')

    def set_authors(self, authors):
        """Sets the author/s for the mapping"""

        self.__info.set('X-Authors', authors)

    def get_version(self):
        """Gets the version of the mapping"""

        return self.__info.get('X-Version')

    def set_version(self, version):
        """Sets the version of the mapping"""

        self.__info.set('X-Version', version)

    def get_mapping(self):
        """Gets the wminput config code"""

        return self.__mapping
        
    def set_mapping(self, mapping):
        """Sets the wminput config code"""

        self.__mapping = mapping
        
    def write(self, dest_path=None):
        """
        Saves the mapping object by writing the files in the mapping directory.

        The metadata it's saved in Mapping.info_filename file.
        The wminput config code it's saved in Mapping.mapping_filename file.
        The associated icon it's copied to the mapping directory.
        """
        if not dest_path:
            if not self.__path:
                raise MappingError, _('No path provided for writing mapping')
            dest_path = self.__path
        elif not os.path.exists(dest_path):
            os.mkdir(dest_path)

        icon_path = self.get_icon()
        icon_filename = os.path.basename(icon_path)
        if not icon_path == os.path.join(dest_path, icon_filename):
            shutil.copy(icon_path, dest_path)
            self.set_icon(icon_filename)
            
        self.__info.write(os.path.join(dest_path, Mapping.info_filename))
        
        mapping_fp = open(os.path.join(dest_path, Mapping.mapping_filename), 'w')
        mapping_fp.write(self.__mapping)
        mapping_fp.close()

        # Clean not useful files
        for item in [x for x in os.listdir(dest_path) if not x in \
                [Mapping.info_filename, Mapping.mapping_filename, icon_filename]]:
            os.unlink(os.path.join(dest_path, item))

        self.__path = dest_path
        
    def __repr__(self):
        return "Mapping <" + self.__info.get('Name', locale=False) + ' ' + \
            str(self.__info.getVersion()) + ">"

class MappingError(exceptions.Exception):
    pass
