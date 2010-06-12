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
        self.__pid = None

    @threaded
    def start(self):
        cmd = self.wminput_cmd
        if self.config_file:
            cmd += ['-c', self.config_file]
        if self.daemon:
            cmd += ['-d']

        #TODO: Maybe exception tracking it's required here
        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        self.__pid = proc.pid
        self.emit('wminput_launched', self.__pid)
        retcode = proc.wait()
        self.emit('wminput_stopped', retcode)

    @gobject.property
    def running(self):
        return self.__pid is not None

    def stop(self):
        # FIXME: That's awful!
        if self.running:
            try:
                os.kill(self.__pid, signal.SIGTERM)
            except:
                pass

            self.__pid = None

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
    #gobject.timeout_add(5000, stopit, x)
    gobject.MainLoop().run()
