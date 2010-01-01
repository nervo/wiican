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

BASE_DATA_DIR = os.getcwd()
if os.path.exists('/usr/share/wiican/'):
    BASE_DATA_DIR = '/usr/share/wiican/'

WMINPUT_CMD = ['/usr/bin/wminput', '-w']

USER_CONFIG_DIR = '.wiican'
CONFIG_SKEL = os.path.join(BASE_DATA_DIR, 'config_skel')

ICON_ON = os.path.join(BASE_DATA_DIR, 'img/wiitrayon.svg')
ICON_OFF = os.path.join(BASE_DATA_DIR, 'img/wiitrayoff.svg')
ICON_DEFAULT = os.path.join(BASE_DATA_DIR, 'img/wiitrayon.svg')

ICON_CONN1 = os.path.join(BASE_DATA_DIR, 'img/wiitrayon1.svg')
ICON_CONN2 = os.path.join(BASE_DATA_DIR, 'img/wiitrayon2.svg')
ICON_CONN3 = os.path.join(BASE_DATA_DIR, 'img/wiitrayon3.svg')

ABOUT_DLG = os.path.join(BASE_DATA_DIR, 'about.ui')
MAPPING_UI = os.path.join(BASE_DATA_DIR, 'mapping.ui')
ENTRY_UI = os.path.join(BASE_DATA_DIR, 'entry.ui')

MAPPING_DEFAULT_VALUES = {
        'name': 'No name', 
        'description': '',
        'icon': ICON_DEFAULT,
        'position': -1,
        'visible': True}
