#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
        name='wiican',
        version='0.1',
        description='Wiimote manager',
        long_description='Wiican its a systray that wrappers wminput',
        author='J. Félix Ontañón',
        author_email='felixonta@gmail.com',
        url='http://dev.emergya.info/projects/show/wiican',

        classifiers=[
            'Development Status :: 0.1.0 - Alpha',
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
        scripts = ['bin/wiican'],
        data_files = [('share/wiican/config_skel', 
                        ['config_skel/mouse.wminput', 
                        'config_skel/neverball.wminput']),
                      ('share/wiican/img', 
                          ['img/wiitrayoff.png', 'img/wiitrayon.png', 
                          'img/wiitrayon1.png', 'img/wiitrayon2.png', 
                          'img/wiitrayon3.png']),
                      ('share/wiican', 
                          ['about.glade','mapping.glade','entry.glade']),
                      ('share/applications', ['wiican.desktop']),
                      ('share/pixmaps', ['wiican.png'])]
)
