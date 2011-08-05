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
for filename in ['data/org.gnome.wiican.service', 'wiican/defs.py']:
    infile = open(filename + '.in', 'r')
    data = infile.read().replace('@PREFIX@', prefix)
    infile.close()

    outfile = open(filename, 'w')
    outfile.write(data)
    outfile.close()

PO_DIR = 'po'
MO_DIR = os.path.join('build', 'mo')

class BuildData(build):
    def run (self):
        build.run (self)

        for po in glob.glob (os.path.join (PO_DIR, '*.po')):
            lang = os.path.basename(po[:-3])
            mo = os.path.join(MO_DIR, lang, 'wiican.mo')

            directory = os.path.dirname(mo)
            if not os.path.exists(directory):
                info('creating %s' % directory)
                os.makedirs(directory)

            if newer(po, mo):
                info('compiling %s -> %s' % (po, mo))
                try:
                    rc = subprocess.call(['msgfmt', '-o', mo, po])
                    if rc != 0:
                        raise Warning, "msgfmt returned %d" % rc
                except Exception, e:
                    error("Building gettext files failed.  Try setup.py \
                        --without-gettext [build|install]")
                    error("Error: %s" % str(e))
                    sys.exit(1)

class InstallData(install_data):
    def run (self):
        self.data_files.extend (self._find_mo_files ())
        install_data.run (self)

    def _find_mo_files (self):
        data_files = []

        for mo in glob.glob (os.path.join (MO_DIR, '*', 'wiican.mo')):
            lang = os.path.basename(os.path.dirname(mo))
            dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES')
            data_files.append((dest, [mo]))

        return data_files

setup(
        name='wiican',
        version='0.3.2',
        description='Wiimote connection and mapping manager',
        long_description='WiiCan assists on configuration and management of ' + \
            'your wiimote under GNU/Linux. It tracks bluetooth connectivity ' + \
            'and allows to use and create mappings to adapt your wiimote for ' + \
            'use on any application.',
        author='J. Félix Ontañón',
        author_email='fontanon@emergya.es',
        url='http://fontanon.org/wiican',

        classifiers=[
            'Development Status :: 0.3.2 - Beta',
            'Environment :: Desktop Environment',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX',
            'Programming Language :: Python',
	    'Topic :: Desktop Environment :: Gnome',
	    'Topic :: Utilities'],
        keywords = ['wii', 'wiimote', 'joystick', 'gamepad', 'cwiid', 'wminput'],
        requires = ['PyGTK', 'dbuspython', 'ply'],

        packages = ['wiican', 'wiican.ui', 'wiican.service', 'wiican.mapping'],
        package_dir =  {'wiican': 'wiican', 'wiican.ui': 'wiican/ui', 
            'wiican.service': 'wiican/service', 'wiican.mapping': 'wiican/mapping'},
            
        scripts = ['bin/wiican', 'bin/wiican-service'],
        
        cmdclass={'build': BuildData, 'install_data': InstallData},
        
        data_files = [('share/wiican/mappings_base', ['data/mappings_base/README']),

                      ('share/wiican/WiiPackages', glob.glob('data/WiiPackages/*')),
                      
                      # Need to call gtk-update-icon-cache -f -t $(datadir)/icons/hicolor
                      # after installing icons
                      ('share/icons/hicolor/16x16/devices', glob.glob('data/icons/16x16/devices/*')),
                      ('share/icons/hicolor/22x22/devices', glob.glob('data/icons/22x22/devices/*')),
                      ('share/icons/hicolor/32x32/devices', glob.glob('data/icons/32x32/devices/*')),
                      ('share/icons/hicolor/48x48/devices', glob.glob('data/icons/48x48/devices/*')),
                      ('share/icons/hicolor/scalable/devices', glob.glob('data/icons/scalable/devices/*')),
                      ('share/icons/hicolor/24x24/status', glob.glob('data/icons/24x24/status/*')),
                      ('share/icons/hicolor/scalable/mimetypes', glob.glob('data/icons/scalable/mimetypes/*')),

                      ('share/dbus-1/services', ['data/org.gnome.wiican.service']),

                      ('share/wiican', ['data/wiimotemanager.ui','data/mapping.ui']),

                      ('share/applications', ['data/wiican.desktop']),
                      ('share/pixmaps', ['data/wiican.svg']),

                      ('share/mime/packages', ['data/mime/wiican.xml']),

                      ('/etc/gconf/schemas', ['data/wiican.schemas']),

                      ('/lib/udev/rules.d', ['data/udev-rules/99-uinput.rules'])
                      ]
)
