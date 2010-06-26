#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, platform
import glob
import subprocess

from distutils.core import setup
from distutils.command.build import build
from distutils.command.install_data import install_data
from distutils.log import warn, info, error, fatal
from distutils.dep_util import newer

# Get current Python version
python_version = platform.python_version_tuple()

# Setup the default install prefix
prefix = sys.prefix

# Check our python is version 2.6 or higher
if python_version[0] >= 2 and python_version[1] >= 6:
    ## Set file location prefix accordingly
    prefix = '/usr/local'

# Get the install prefix if one is specified from the command line
for arg in sys.argv:
    if arg.startswith('--prefix='):
        prefix = arg[9:]
        prefix = os.path.expandvars(prefix)

# Gen .in files with @PREFIX@ replaced
for filename in ['org.gnome.wiican.service', 'wiican/defs.py']:
    infile = open(filename + '.in', 'r')
    data = infile.read().replace('@PREFIX@', prefix)
    infile.close()

    outfile = open(filename, 'w')
    outfile.write(data)
    outfile.close()

setup(
        name='wiican',
        version='0.3',
        description='Wiimote manager',
        long_description='Wiican its a systray that wrappers wminput',
        author='J. Félix Ontañón',
        author_email='felixonta@gmail.com',
        url='http://launchpad.net/wiican',

        classifiers=[
            'Development Status :: 0.3 - Alpha',
            'Environment :: Desktop Environment',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX',
            'Programming Language :: Python',
	    'Topic :: Desktop Environment :: Gnome',
	    'Topic :: Utilities'],
        keywords = ['wii', 'wiimote', 'joystick', 'gamepad', 'cwiid', 'wminput'],
        requires = ['PyGTK', 'dbuspython', 'PyYAML'],

        packages = ['wiican'],
        scripts = ['bin/wiican', 'bin/wiican-service'],
        data_files = [('share/wiican/config_skel', 
                        ['config_skel/mouse.wminput', 
                        'config_skel/neverball.wminput']),
                      ('share/wiican/img', 
                          ['img/wiitrayoff.svg', 'img/wiitrayon.svg',
                          'img/wiitrayon1.svg', 'img/wiitrayon2.svg', 
                          'img/wiitrayon3.svg']),
                      ('share/dbus-1/services',
                          ['org.gnome.wiican.service']),
                      ('share/wiican', 
                          ['wiimotemanager.ui','mapping.ui', 'wiican.svg']),
                      ('share/applications', ['wiican.desktop']),
                      ('share/pixmaps', ['wiican.svg'])]
)
