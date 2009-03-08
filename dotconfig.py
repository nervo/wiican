import os
import shutil
import fnmatch
import re
import exceptions
import yaml

def get_mapping_file_metadata(file_path):
    metadata_block = ''

    fp = open(file_path, 'r')
    line = fp.readline().strip()
    while line:
        if line.startswith('#'):
            metadata_block += line[1:]+'\n'
        line = fp.readline().strip()
    fp.close()

    return yaml.load(metadata_block)

def get_mapping_file(file_path):
    mapping_block = ''
    fp = open(file_path, 'r')
    line = fp.readline()
    while line:
        if not line.strip().startswith('#'):
            mapping_block += line
        line = fp.readline()
    fp.close()

    return mapping_block

def set_mapping_file_metadata(file_path, **kwargs):
    mapping = ''
    fp = open(file_path, 'r')
    line = fp.readline()
    while line:
        if not line.startswith('#'):
            mapping += line
        line = fp.readline()
    fp.close()

    fp = open(file_path, 'w')
    fp.write('## Wiizard Config file for wminput\n')
    for meta in yaml.dump(kwargs, default_flow_style=False).split('\n')[:-1]:
        fp.write('# ' + meta + '\n')
    fp.write(mapping)
    fp.close()


#TODO: Maybe a Singleton or Borg pattern?
class DotConfig:
    def __init__(self, dotdir, skeldir=None):
        self.dotdir = dotdir
        self.skeldir = skeldir

    def get_files(self, mask='*'):
        dotdir_path = self.__create_dotdir()
        dotfiles = []

        for root, dir, files in os.walk(dotdir_path):
            match_files = fnmatch.filter(files, mask)
            dotfiles += [os.path.join(root, file) for file in match_files]

        return dotfiles

    def __create_dotdir(self):
        dotdir_path = os.path.join(os.environ["HOME"], self.dotdir)

        if not os.path.exists(dotdir_path) and self.skeldir:
            if not os.path.exists(self.skeldir):
                raise DotConfigError, "Skel config dir doesn't exists"
            else:
                shutil.copytree(self.skeldir, dotdir_path)

        return dotdir_path


class DotConfigError(exceptions.Exception):
    def __init__(self, args=None):
        self.args = args

    def __str__(self):
        return repr(self.args)
