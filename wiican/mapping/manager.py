# -*- coding: utf-8 -*-
# vim: ts=4
###
#
# Copyright (c) 2009-2011 J. Félix Ontañón
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

import os
import shutil
import tarfile
import tempfile
import exceptions
import random
import copy

from wiican.utils import Singleton, GConfStore
from wiican.mapping.mapping import Mapping
from wiican.defs import GCONF_KEY, MAPPINGS_HOME_DIR, MAPPINGS_BASE_DIR, \
    INIT_PACKAGES
   
class MappingManager(Singleton, GConfStore):
    """
    Handles one-shot mapping manager instance (singleton).

    The MappingManager allows scan mappings from the system and user data paths, 
    and perform a bunch of operation with mappings.

    The MappingManager object offers some python dict methods allowing to get/set
    attributes, iteration, deletion and check size (number of mappings managed).
    """
    
    defaults = {'mapping_sort': [], 'mapping_visible': set([])}
   
    def __init__(self):
        """Gets the single mapping manager instance"""
        
        Singleton.__init__(self)
        GConfStore.__init__(self, GCONF_KEY)

        self.home_path = MAPPINGS_HOME_DIR
        self.system_paths = MAPPINGS_BASE_DIR

        if not type(self.system_paths) is list:
            self.system_paths = [self.system_paths]

        self.__mapping_bag = {}
        self.loadconf(only_defaults=True)
        self.options['mapping_visible'] = set(self.options['mapping_visible'])

    def scan_mappings(self):
        """
        Scan mappings from default system and user data directories.
        Auto-import the initial wiican mapping packages into user data dir if it
        doesn't exists.
        
        Mappings are distinguished by dirname. If a system mapping has the same 
        dirname as the user data dir, the system mapping it's ignored.
        """
        
        def load_mapping(mappings, dirname, fnames):
            if Mapping.info_filename in fnames and Mapping.mapping_filename in fnames:
                mapping_id = os.path.splitext(os.path.basename(dirname))[0]
                mappings[mapping_id] = Mapping(dirname)
                if not mapping_id in self.options['mapping_sort']:
                    self.options['mapping_sort'].append(mapping_id)

        # Import INIT_PACKAGES into home_path at first run
        if not os.path.exists(self.home_path):
            os.mkdir(self.home_path)

            for package_path in [x for x in INIT_PACKAGES if os.path.exists(x)]:
                self.import_mapping(package_path)

        # Load first system mappings, then user mappings.
        # If same mapping_id, the user mapping remains.
        for path in self.system_paths + [self.home_path]:
            os.path.walk(path, load_mapping, self.__mapping_bag)

        self.options['mapping_sort'] = [x for x in self.options['mapping_sort'] \
            if x in self.__mapping_bag.keys()]

        self.options['mapping_visible'] = set([x for x in \
            self.options['mapping_visible'] if x in self.__mapping_bag.keys()])

    def import_mapping(self, package_path):
        """Import a wiican mapping package into user data dir"""

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
        """Export a mapping as a wiican mapping package"""

        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        mapping = copy.copy(self.__mapping_bag[mapping_id])
        package_file = tarfile.TarFile(dest_filepath, 'w')

        # Write into a temp dir to avoid the user for saving a system mapping.
        mapping_tmp_path = tempfile.mkdtemp()
        mapping.write(mapping_tmp_path)

        for f in os.listdir(mapping_tmp_path):
            package_file.add(os.path.join(mapping_tmp_path, f), arcname=f)
            
        package_file.close()
        shutil.rmtree(mapping_tmp_path)
        
    def add_new_mapping(self, mapping):
        """Add a mapping to be controlled by mapping manager"""
        
        mapping_id = self.__gen_unique_mapping_id()
        mapping_path = os.path.join(self.home_path, mapping_id)
        mapping.write(mapping_path)
        self.__mapping_bag[mapping_id] = mapping
        self.options['mapping_sort'].append(mapping_id)
        self.options['mapping_visible'].add(mapping_id)

        return mapping_id

    def write_mapping(self, mapping):
        """Write a mapping to disk"""
        
        if os.path.dirname(mapping.get_path()) in self.system_paths:
            return self.add_new_mapping(copy.copy(mapping))
        else:
            mapping.write()
            return False

    def swap_mapping_order(self, mapping_id1, mapping_id2, after=False):
        """Swaps mapping_id2 before mapping_id1"""
        
        if not mapping_id1 in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id1
        
        if not mapping_id2 in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id2

        if mapping_id1 == mapping_id2: return

        sort_list = copy.copy(self.options['mapping_sort'])
        sort_list.remove(mapping_id2)
        index = sort_list.index(mapping_id1)

        if after: 
            sort_list = sort_list[0:index+1] + [mapping_id2] + sort_list[index+1:]
        else: 
            sort_list.insert(index, mapping_id2)

        self.options['mapping_sort'] = sort_list

    def is_system_mapping(self, mapping_id):
        """Check if the mapping (identified by mapping_id) it's a system mapping"""
        
        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        return os.path.dirname(self.__mapping_bag[mapping_id].get_path()) in self.system_paths
            
    def is_visible(self, mapping_id):
        """Check if the mapping (identified by mapping_id) it's marked as visible"""

        if not mapping_id in self.__mapping_bag:
            raise MappingManagerError, _('Mapping not found:') + ' ' + mapping_id

        return mapping_id in self.options['mapping_visible']
        
    def set_visible(self, mapping_id, visible):
        """Mark a mapping (identified by mapping_id) as visible or invisible"""

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

        if os.path.dirname(self.__mapping_bag[mapping_id].get_path()) in self.system_paths:
            raise MappingManagerError, _('Cannot remove a system installed mapping')

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

    def __len__(self):
        return len(self.__mapping_bag)

    def items(self):
        for mapping_id in self.options['mapping_sort']:
            yield mapping_id, self.__mapping_bag[mapping_id]

    def __repr__(self):
        return self.__mapping_bag.__repr__()

class MappingManagerError(exceptions.Exception):
    pass
