import os.path
import shutil
import exceptions

from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath

from wiican.defs import ICON_DEFAULT

class Mapping(object):
    info_filename = 'info.desktop'
    mapping_filename = 'mapping.wminput'
    
    def __init__(self, path=None):
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
        return self.__path

    def get_name(self):
        return self.__info.getName()
        
    def set_name(self, name):
        self.__info.set('Name', name)
        self.__info.set('Name', name, locale=True)

    def get_comment(self):
        return self.__info.getComment()

    def set_comment(self, comment):
        self.__info.set('Comment', comment)
        self.__info.set('Comment', comment, locale=True)

    def get_icon(self):
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
        self.__info.set('Icon', icon_path)

    def get_authors(self):
        return self.__info.get('X-Authors')

    def set_authors(self, authors):
        self.__info.set('X-Authors', authors)

    def get_version(self):
        return self.__info.get('X-Version')

    def set_version(self, version):
        self.__info.set('X-Version', version)

    def get_mapping(self):
        return self.__mapping
        
    def set_mapping(self, mapping):
        self.__mapping = mapping
        
    def write(self, dest_path=None):
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
