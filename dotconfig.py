import os
import shutil
import fnmatch
import exceptions

DEFAULT_ICON = 'img/wiitrayon.png'

def get_mapping_file_metadata(file_path):
    metadata = {'icon': DEFAULT_ICON, 'name': 'no name', 'description': ''}
    fp = open(file_path, 'r')

    line = fp.readline().strip()
    while line:
        if line.startswith('#') and ':' in line:
            (metakey, metavalue) = line[1:].split(':')
            if metadata.has_key(metakey.strip().lower()):
                metadata[metakey.strip().lower()] = metavalue.strip()
        line = fp.readline().strip()

    fp.close()
    return metadata

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
