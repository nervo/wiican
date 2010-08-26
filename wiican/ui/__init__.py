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

from os.path import expanduser
from wiican.utils import Singleton, GConfStore
from wiican.defs import GCONF_KEY, MAPPING_PACKAGES_BASE_DIR

class UIPrefStore(Singleton, GConfStore):

    defaults = {
        'mapping_dlg_width': 500,
        'mapping_dlg_height': 400,
        'import_dir': expanduser(MAPPING_PACKAGES_BASE_DIR),
        'export_dir': expanduser("~/"),
        'icon_dir': '/usr/share/icons'
    }

    def __init__(self):
        Singleton.__init__(self)
        GConfStore.__init__(self, GCONF_KEY)

    def loadconf(self):
        GConfStore.loadconf(self, only_defaults=True)

from notificator import Notificator
from pnganimation import PngAnimation
from editordlg import MappingEditorDialog
from managerdlg import MappingManagerDialog
