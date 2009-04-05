import os.path

BASE_DATA_DIR = '/usr/share/wiizard/'
WMINPUT_CMD = ['/usr/bin/wminput', '-w']

USER_CONFIG_DIR = '.wiizard'
CONFIG_SKEL = os.path.join(BASE_DATA_DIR, 'config_skel')

ICON_ON = os.path.join(BASE_DATA_DIR, 'img/wiitrayon.png')
ICON_OFF = os.path.join(BASE_DATA_DIR, 'img/wiitrayoff.png')
ICON_DEFAULT = os.path.join(BASE_DATA_DIR, 'img/wiitrayon.png')

ICON_CONN1 = os.path.join(BASE_DATA_DIR, 'img/wiitrayon1.png')
ICON_CONN2 = os.path.join(BASE_DATA_DIR, 'img/wiitrayon2.png')
ICON_CONN3 = os.path.join(BASE_DATA_DIR, 'img/wiitrayon3.png')

ABOUT_DLG = os.path.join(BASE_DATA_DIR, 'about.glade')
MAPPING_GLADE = os.path.join(BASE_DATA_DIR, 'mapping.glade')
ENTRY_GLADE = os.path.join(BASE_DATA_DIR, 'entry.glade')

MAPPING_DEFAULT_VALUES = {
        'name': 'No name', 
        'description': '',
        'icon': ICON_DEFAULT,
        'position': -1,
        'visible': True}
