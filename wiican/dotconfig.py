# -*- coding: utf-8 -*-
# vim: ts=4 
###
#
# Wiican is the legal property of J. Félix Ontañón <felixonta@gmail.com>
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###

import os
import shutil
import fnmatch
import re
import random
import exceptions
import yaml

def read_metadata(file_path):
    metadata_block = ''

    fp = open(file_path, 'r')
    line = fp.readline().strip()
    while line:
        if line.startswith('#'):
            metadata_block += line[1:]+'\n'
        line = fp.readline().strip()
    fp.close()

    return yaml.load(metadata_block) or {}

def read_mapping(file_path):
    mapping_block = ''
    fp = open(file_path, 'r')
    line = fp.readline()
    while line:
        if not line.strip().startswith('#'):
            mapping_block += line
        line = fp.readline()
    fp.close()

    return mapping_block

def write_mapping(file_path, mapping=None, **kwargs):
    fp = open(file_path, 'w')
    fp.write('## Wiican Config file for wminput\n')

    for meta in yaml.dump(kwargs, default_flow_style=False).split('\n')[:-1]:
        fp.write('# ' + meta + '\n')

    if mapping:
        fp.write(re.sub(r'##*','##', mapping))

    fp.close()

def remove_mapping(file_path, remove_icon=False):
    #TODO: Try-except block required here
    if remove_icon:
        icon_path = read_metadata(file_path)['icon']
        os.unlink(icon_path)

    os.unlink(file_path)

#TODO: Maybe a Singleton or Borg pattern?
class DotConfig:
    #TODO: mark as static? 
    seed = 'abcdef0123456789'
    long = 4

    def __init__(self, dotdir, skeldir=None):
        self.dotdir = dotdir
        self.skeldir = skeldir

    def get_files(self, mask='*', ignore_non_readable=False):
        dotdir_path = self.__create_dotdir()
        dotfiles = []

        for root, dir, files in os.walk(dotdir_path):
            match_files = map(lambda file: os.path.join(root, file), 
                    fnmatch.filter(files, mask))
            dotfiles += [file for file in match_files \
                    if not ignore_non_readable or \
                    os.access(os.path.join(root, file), os.R_OK)]

        return dotfiles

    def new_filename(self, prefix=None, suffix=None):
        def rand_filename(prefix, suffix):
            filename = ''.join(
                    [random.choice(self.seed) for x in xrange(self.long)])

            if prefix:
                filename = prefix + filename
            if suffix:
                filename += suffix
            return filename

        while True:
            filename = rand_filename(prefix, suffix)
            if not os.path.exists(self.dotdir + os.sep + filename):
                break

        return os.environ["HOME"]+os.sep+self.dotdir+os.sep+filename.lower()

    def __create_dotdir(self):
        dotdir_path = os.path.join(os.environ["HOME"], self.dotdir)

        if not os.path.exists(dotdir_path) and self.skeldir:
            if not os.path.exists(self.skeldir):
                raise DotConfigError, _("Skel config dir doesn't exists")
                return None
            else:
                shutil.copytree(self.skeldir, dotdir_path)
        elif not os.access(dotdir_path, os.X_OK) \
          or not os.access(dotdir_path, os.R_OK):
            raise DotConfigError, _("Wrong perms on user config dir")
            return None

        return dotdir_path


class DotConfigError(exceptions.Exception):
    def __init__(self, args=None):
        self.args = args

    def __str__(self):
        return repr(self.args)