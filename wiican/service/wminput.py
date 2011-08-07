# -*- coding: utf-8 -*-
# vim: ts=4
###
#
# Copyright (c) 2009-2011 J. Félix Ontañón
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
# Authors : J. Félix Ontañón <fontanon@emergya.es>
#
###

import os
import gobject
import threading
import subprocess
import signal

gobject.threads_init()

def threaded(f):
    def wrapper(*args):
        t = threading.Thread(target=f, args=args)
        t.setDaemon(True)
        t.start()
    return wrapper

class WMInputLauncher(gobject.GObject):
    __gsignals__ = {
        'wminput_launched'  : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                      (gobject.TYPE_PYOBJECT,)),
        'wminput_stopped'   : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                                      (gobject.TYPE_PYOBJECT,))
     }

    wminput_cmd = ['wminput']

    def __init__(self, config_file=None, daemon=False):
        super(WMInputLauncher, self).__init__()

        if config_file and not os.path.exists(config_file):
            raise 'Not config file found:', self.config_file

        self.config_file = config_file
        self.daemon = daemon
        self._process = None

    @threaded
    def start(self):
        cmd = []
        if self.config_file:
            cmd += ['-c', self.config_file]
        if self.daemon:
            cmd += ['-d']

        #TODO: Maybe exception tracking it's required here
        self._process = subprocess.Popen(self.wminput_cmd + cmd, stdout=subprocess.PIPE)
        self.emit('wminput_launched', self._process.pid)
        retcode = self._process.wait()
        self.emit('wminput_stopped', retcode)

    @gobject.property
    def running(self):
        return self._process is not None

    def stop(self):
        if self.running:
            self._process.terminate()
            self._process = None

if __name__ == '__main__':
    def loaded(wminput, pid):
        print 'Launched:', pid

    def stopped(wminput, retcode):
        print 'Stopped:', retcode

    def stopit(x):
        print 'Stopping it'
        if x.running:
            print 'Still running'
            x.stop()

    x = WMInputLauncher(daemon=True)
    x.connect('wminput_launched', loaded)
    x.connect('wminput_stopped', stopped)
    x.start()
    gobject.timeout_add(5000, stopit, x)
    gobject.MainLoop().run()
