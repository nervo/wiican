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
import exceptions
import random

from wiican.defs import GCONF_KEY, MAPPINGS_HOME_DIR, MAPPINGS_BASE_DIR
from wiican.utils import Borg, GConfStore
from wiican.mapping.mapping import Mapping

class MappingManager(Borg, GConfStore):
    defaults = {'mapping_sort': [], 'mapping_visible': set([])}
    
    def __init__(self):
        Borg.__init__(self)
        GConfStore.__init__(self, GCONF_KEY)
        
        self.home_path = MAPPINGS_HOME_DIR
        self.system_paths = MAPPINGS_BASE_DIR
        
        if not type(self.system_paths) is list:
            self.system_paths = [self.system_paths]

        self.__mapping_bag = {}
        self.loadconf()
        self.options['mapping_visible'] = set(self.options['mapping_visible'])
        
    def scan_mappings(self):
        def load_mapping(mappings, dirname, fnames):
            if Mapping.info_filename in fnames and Mapping.mapping_filename in fnames:
                mapping_id = os.path.splitext(os.path.basename(dirname))[0]
                mappings[mapping_id] = Mapping(dirname)
                if not mapping_id in self.options['mapping_sort']:
                    self.options['mapping_sort'].append(mapping_id)

        for path in self.system_paths + [self.home_path]:
            os.path.walk(path, load_mapping, self.__mapping_bag)

        self.options['mapping_sort'] = [x for x in self.options['mapping_sort'] \
            if x in self.__mapping_bag.keys()]

        self.options['mapping_visible'] = set([x for x in \
            self.options['mapping_visible'] if x in self.__mapping_bag.keys()])

    def import_mapping(self, package_path):
        package_file = tarfile.open(package_path)
        
        if not Mapping.info_filename in package_file.getnames():
            raise MappingManagerError, _('Not %s file found on wiican package' % \
                Mapping.info_filename)
    
        if not Mapping.mapping_filename in package_file.getnames():
            raise MappingManagerError, _('Not %s file found  on wiican package' % \
                Mapping.mapping_filename)

        mapping_id = self.__gen_unique_mapping_id()
        mapping_path = os.path.join(self.home_path, mapping_id)
        
        package_file.extractall(mapping_path)
        package_file.close()

        mapping = Mapping(mapping_path)
 
        self.__mapping_bag[mapping_id] = mapping
        self.options['mapping_sort'].append(mapping_id)
        self.options['mapping_visible'].add(mapping_id)        
            
        return mapping_id

    def export_mapping(self, mapping_id, dest_filepath):
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        mapping = self.__mapping_bag[mapping_id]
        mapping_path = self.__mapping_bag[mapping_id].get_path()
        package_file = tarfile.TarFile(dest_filepath, 'w')

        mapping.write()

        for f in os.listdir(mapping_path):
            package_file.add(os.path.join(mapping_path, f), arcname=f)
            
        package_file.close()

    def add_new_mapping(self, mapping):
        mapping_id = self.__gen_unique_mapping_id()
        mapping_path = os.path.join(self.home_path, mapping_id)
        mapping.write(mapping_path)
        self.__mapping_bag[mapping_id] = mapping
        self.options['mapping_sort'].append(mapping_id)
        self.options['mapping_visible'].add(mapping_id)        
                
        return mapping_id

    def swap_mapping_order(self, mapping_id1, mapping_id2):
        if not mapping_id1 in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id1
        
        if not mapping_id2 in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id2

        index = self.options['mapping_sort'].index(mapping_id1)
        self.options['mapping_sort'].remove(mapping_id2)
        self.options['mapping_sort'].insert(index, mapping_id2)

    def is_visible(self, mapping_id):
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        return mapping_id in self.options['mapping_visible']
        
    def set_visible(self, mapping_id, visible):
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        if visible:
            self.options['mapping_visible'].add(mapping_id)
        else:   
            self.options['mapping_visible'].remove(mapping_id)

    def __gen_unique_mapping_id(self):
        mapping_id = str(random.randint(1,999999))
        while True:
            if os.path.exists(os.path.join(self.home_path, mapping_id)):
                mapping_id = str(random.randint(1,999999))
            else: break
            
        return mapping_id

    def __delitem__(self, mapping_id):
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id
    
        mapping_path = self.__mapping_bag[mapping_id].get_path()
        shutil.rmtree(mapping_path)
        self.options['mapping_sort'].remove(mapping_id)
        if mapping_id in self.options['mapping_visible']:
            self.options['mapping_visible'].remove(mapping_id)
        self.__mapping_bag.pop(mapping_id)

    def __getitem__(self, mapping_id):
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        return self.__mapping_bag[mapping_id]

    def __setitem__(self, mapping_id, mapping):
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        self.__mapping_bag[mapping_id] = mapping

    def __iter__(self):
        for mapping_id in self.options['mapping_sort']:
            yield mapping_id

    def items(self):
        for mapping_id in self.options['mapping_sort']:
            yield mapping_id, self.__mapping_bag[mapping_id]

    def __repr__(self):
        return self.__mapping_bag.__repr__()

class MappingManagerError(exceptions.Exception):
    pass