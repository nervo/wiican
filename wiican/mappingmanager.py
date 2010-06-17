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
import os
import tarfile
import tempfile
import exceptions

from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath
from xdg.BaseDirectory import xdg_cache_home

from defs import ICON_DEFAULT

class Mapping(object):
    def __init__(self, name='', comment='', version='', authors='', 
            icon_path='', mapping_path=''):
        
        self.name = name
        self.comment = comment
        self.version = version
        self.authors = authors
        self.icon_path = icon_path
        self.mapping_path = mapping_path

class MappingPackage(object):
    pattern = '*.tgz'

    @staticmethod
    def load(package_path):
        package_filename = os.path.splitext(os.path.basename(package_path))[0]
        extract_path = os.path.join(xdg_cache_home, 'wiican', package_filename)

        package_file = tarfile.open(package_path)
        
        if not 'info.desktop' in package_file.getnames():
            raise MappingPackageError, 'Not info.desktop file found'
    
        if not 'mapping.wminput' in package_file.getnames():
            raise MappingPackageError, 'Not mapping.wminput file found'

        package_file.extractall(extract_path)

        # Get freedesktop definition file
        info = DesktopEntry()
        info.parse(os.path.join(extract_path, 'info.desktop'))
        
        # Get icon file path
        icon_name = info.getIcon()
        if icon_name in package_file.getnames(): # Icon included
            icon_path = info.parse(os.path.join(extract_path, icon_name))
        elif getIconPath(icon_name): # Theme icon
            icon_path = getIconPath(icon_name)
        else:
            icon_path = ICON_DEFAULT # Default icon

        # Get wminput mapping definition file path
        mapping_file = os.path.join(extract_path, 'mapping.wminput')
        
        package_file.close()

        return Mapping(info.getName(), info.getComment(), info.getVersion(), 
            info.get('X-Authors'), icon_path, mapping_file)
        
    @staticmethod
    def save(mapping, mapping_path):
        pass

class MappingPackageError(exceptions.Exception):
    pass


import glob

class MappingManager(object):
    def __init__(self, user_paths=[], system_paths=[]):

        self.user_paths = user_paths
        self.system_paths = system_paths

        if not type(self.user_paths) is list:
            self.user_paths = [self.user_paths]
            
        if not type(self.system_paths) is list:
            self.system_paths = [self.system_paths]
        
        self.mappings = {}
            
    def scan_mappings(self):
        new_mappings = {}
        for path in self.system_paths + self.user_paths:
            for mapping_path in glob.glob(os.path.join(path, MappingPackage.pattern)):
                package_filename = os.path.splitext(os.path.basename(package_path))[0]
                new_mappings.update({package_filename: MappingPackage.load(mapping_path)})
                
        new_mappings.update(self.mappings)
        self.mappings = new_mappings

    def install(self, mapping_name):
        pass
        
    def remove(self, mapping_name):
        pass
        
    def get_mapping_list(self):
        pass
        
    def get_mapping(self):
        pass
