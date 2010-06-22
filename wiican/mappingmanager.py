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
import shutil
import tarfile
import tempfile
import exceptions
import random

from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath
from xdg.BaseDirectory import save_data_path

from defs import ICON_DEFAULT, BASE_DATA_DIR

class Mapping(object):
    def __init__(self, info_path=None, mapping_path=None):
        # Get freedesktop definition file
        self.__info = DesktopEntry()
        
        if info_path:
            self.__info.parse(info_path)
        else:
            self.__info.new('info.desktop')
            self.__info.set('Type', 'Wiican Mapping')
            
        if mapping_path:
            mapping_fp = open(mapping_path, 'r')
            self.__mapping = mapping_fp.read()
            mapping_fp.close()
        else:
            self.__mapping = ''

        # Get icon file path
        icon_name = self.__info.getIcon()
        if info_path and icon_name in os.listdir(os.path.dirname(info_path)): # Icon included
            self.set_icon(os.path.join(os.path.dirname(info_path), icon_name))
        elif getIconPath(icon_name): # Theme icon
            self.set_icon(getIconPath(icon_name))
        else:
            self.set_icon(ICON_DEFAULT) # Default icon

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
        return self.__info.getIcon()
                
    def set_icon(self, icon_path):
        self.__info.set('Icon', icon_path)

    def get_authors(self):
        self.__info.get('X-Authors')

    def set_authors(self, authors):
        self.__info.set('X-Authors', authors)

    def get_version(self):
        self.__info.getVersion()

    def set_version(self, version):
        self.__info.setVersion(version)

    def get_mapping(self):
        return self.__mapping
        
    def set_mapping(self, mapping):
        self.__mapping = mapping
        
    def write(self, dest_path):
        if not os.path.exists(dest_path):
            os.mkdir(dest_path)
        else:
            for item in os.listdir(dest_path): 
                os.unlink(os.path.join(dest_path, item))
            
        self.__info.write(os.path.join(dest_path, 'info.desktop'))
        shutil.copy(self.get_icon(), dest_path)
        mapping_fp = open(os.path.join(dest_path, 'mapping.wminput'), 'w')
        mapping_fp.write(self.__mapping)
        mapping_fp.close()

    def __repr__(self):
        return "Mapping <" + self.__info.get('Name', locale=False) + ' ' + \
            str(self.__info.getVersion()) + ">"
        
class MappingManager(object):
    def __init__(self, home_path, system_paths=[]):

        self.home_path = home_path
        self.system_paths = system_paths

        if not type(self.system_paths) is list:
            self.system_paths = [self.system_paths]
        
        self.mapping_bag = {}
            
    def scan(self):
        def load_mapping(mappings, dirname, fnames):
            if 'info.desktop' in fnames and 'mapping.wminput' in fnames:
                mapping_id = os.path.splitext(os.path.basename(dirname))[0]
                mappings[mapping_id] = {'path': dirname, 
                    'mapping': Mapping(os.path.join(dirname, 
                    'info.desktop'), os.path.join(dirname, 'mapping.wminput'))}

        for path in self.system_paths + [self.home_path]:
            os.path.walk(path, load_mapping, self.mapping_bag)

    def install(self, package_path):
        package_file = tarfile.open(package_path)
        
        if not 'info.desktop' in package_file.getnames():
            raise MappingManagerError, 'Not info.desktop file found'
    
        if not 'mapping.wminput' in package_file.getnames():
            raise MappingManagerError, 'Not mapping.wminput file found'

        mapping_id = os.path.splitext(os.path.basename(package_path))[0]
        mapping_path = os.path.join(self.home_path, mapping_id)
        
        package_file.extractall(mapping_path)
        package_file.close()

        mapping = Mapping(os.path.join(mapping_path, 'info.desktop'), 
            os.path.join(mapping_path, 'mapping.wminput'))
 
        self.mapping_bag[mapping_id] = {'path': mapping_path, 'mapping':
            mapping}

    def export(self, mapping_id, dest_path):
        if not mapping_id in self.mapping_bag:
            raise MappingManagerError, 'Mapping not found:' + ' ' + mapping_id

        mapping = self.mapping_bag[mapping_id]['mapping']
        mapping_path = self.mapping_bag[mapping_id]['path']
        package_file = tarfile.TarFile(os.path.join(dest_path, 
            mapping_id+'.tgz'), 'w')

        mapping.write(mapping_path)

        for f in os.listdir(mapping_path):
            package_file.add(os.path.join(mapping_path, f), arcname=f)
            
        package_file.close()

    def add(self, mapping):
        mapping_id = str(random.randint(1,999999))
        while True:
            if os.path.exists(os.path.join(self.home_path, mapping_id)):
                mapping_id = str(random.randint(1,999999))
            else: break

        mapping_path = os.path.join(self.home_path, mapping_id)
        mapping.write(mapping_path)
        self.mapping_bag[mapping_id] = {'path': mapping_path, 'mapping': mapping}
                
        return mapping_id
        
    def remove(self, mapping_id):
        if not mapping_id in self.mapping_bag:
            raise MappingManagerError, 'Mapping not found:' + ' ' + mapping_id
    
        mapping_path = self.mapping_bag[mapping_id]['path']
        shutil.rmtree(mapping_path)
        self.mapping_bag.pop(mapping_id)

    def get_mapping(self, mapping_id):
        if not mapping_id in self.mapping_bag:
            raise MappingManagerError, 'Mapping not found:' + ' ' + mapping_id

        return self.mapping_bag[mapping_id]['mapping']

    def get_mapping_path(self, mapping_id):
        if not mapping_id in self.mapping_bag:
            raise MappingManagerError, 'Mapping not found:' + ' ' + mapping_id

        return self.mapping_bag[mapping_id]['path']
        
mapping_manager = MappingManager(save_data_path('wiican'), BASE_DATA_DIR)

class MappingManagerError(exceptions.Exception):
    pass
