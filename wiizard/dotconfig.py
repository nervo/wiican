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
    fp.write('## Wiizard Config file for wminput\n')

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

    def get_files(self, mask='*'):
        dotdir_path = self.__create_dotdir()
        dotfiles = []

        for root, dir, files in os.walk(dotdir_path):
            match_files = fnmatch.filter(files, mask)
            dotfiles += [os.path.join(root, file) for file in match_files]

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
                raise DotConfigError, "Skel config dir doesn't exists"
            else:
                shutil.copytree(self.skeldir, dotdir_path)

        return dotdir_path


class DotConfigError(exceptions.Exception):
    def __init__(self, args=None):
        self.args = args

    def __str__(self):
        return repr(self.args)
