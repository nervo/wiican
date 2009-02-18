import os
import shutil
import fnmatch
import exceptions

class Borg:
    __shared_state = {}
    def __init__(self):
         self.__dict__ = self.__shared_state

class DotConfig(Borg):
    def __init__(self, dotdir, skeldir=None):
        Borg.__init__(self)

        self.dotdir = dotdir
        self.skeldir = skeldir

    def get_files(self, mask='*'):
        dotdir_path = self.__create_dotdir()
        dotfiles = []

        for root, dir, files in os.walk(dotdir_path):
            match_files = fnmatch.filter(files, mask)
            dotfiles.append([os.path.join(root, file) for file in match_files])

        return dot_files

    def __create_dotdir(self):
        dotdir_path = os.path.join(os.environ["HOME"], self.dotdir)

        if not os.path.exists(dotdir_path) and self.skeldir:
            if not os.path.exists(self.skeldir):
                raise DotConfigError("Skel config dir doesn't exists")
            else:
                shutil.copytree(self.skeldir, dotdir_path)

        return dotdir_path

class DotConfigError(exceptions.Exception):
    def __init__(self, args=None):
        self.args = args
