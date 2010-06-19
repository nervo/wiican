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

from xdg.DesktopEntry import DesktopEntry
from xdg.IconTheme import getIconPath

from defs import ICON_DEFAULT

class Mapping(object):
    def __init__(self, info_path, mapping_path):
        # Get freedesktop definition file
        self.__info = DesktopEntry()
        self.__info.parse(info_path)

        mapping_fp = open(mapping_path, 'r')
        self.mapping = mapping_fp.read()
        mapping_fp.close()

        # Get icon file path
        icon_name = self.__info.getIcon()
        if icon_name in os.listdir(os.path.dirname(info_path)): # Icon included
            self.icon_path = os.path.join(os.path.dirname(info_path), icon_name)
        elif getIconPath(icon_name): # Theme icon
            self.icon_path = getIconPath(icon_name)
        else:
            self.icon_path = ICON_DEFAULT # Default icon
            
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

    def get_authors(self):
        self.__info.get('X-Authors')

    def set_authors(self, authors):
        self.__info.set('X-Authors', authors)

    def get_version(self):
        self.__info.getVersion()

    def set_version(self, version):
        self.__info.setVersion(version)

    def write(self, dest_path):
        self.__info.write(os.path.join(dest_path, 'info.desktop'))
        shutil.copy(self.icon_path, dest_path)
        mapping_fp = open(os.path.join(dest_path, 'mapping.wminput'), 'w')
        mapping_fp.write(self.mapping)
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
                mapping_name = os.path.splitext(os.path.basename(dirname))[0]
                mappings[mapping_name] = {'path': dirname, 
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

        mapping_name = os.path.splitext(os.path.basename(package_path))[0]
        mapping_path = os.path.join(self.home_path, mapping_name)
        
        package_file.extractall(mapping_path)
        package_file.close()

        mapping = Mapping(os.path.join(mapping_path, 'info.desktop'), 
            os.path.join(mapping_path, 'mapping.wminput'))
 
        self.mapping_bag[mapping_name] = {'path': mapping_path, 'mapping':
            mapping}

    def export(self, mapping_name, dest_path):
        if not mapping_name in self.mapping_bag:
            raise MappingManagerError, 'Mapping not found:' + ' ' + mapping_name

        mapping = self.mapping_bag[mapping_name]['mapping']
        mapping_path = self.mapping_bag[mapping_name]['path']
        package_file = tarfile.TarFile(os.path.join(dest_path, 
            mapping_name+'.tgz'), 'w')

        mapping.write(mapping_path)

        for f in os.listdir(mapping_path):
            package_file.add(os.path.join(mapping_path, f), arcname=f)
            
        package_file.close()
        
    def remove(self, mapping_name):
        if not mapping_name in self.mapping_bag:
            raise MappingManagerError, 'Mapping not found:' + ' ' + mapping_name
    
        mapping_path = self.mapping_bag[mapping_name]['path']
        shutil.rmtree(mapping_path)
        self.mapping_bag.pop(mapping_name)

class MappingManagerError(exceptions.Exception):
    pass
