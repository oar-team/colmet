import asyncore
import atexit
import logging
import os
import signal
import sys
from threading import Thread
import time

from pyinotify import ProcessEvent, AsyncNotifier, WatchManager
import pyinotify

LOG = logging.getLogger()


class as_thread(object):
    """Decorator that make any method a thread object."""
    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        _thread = obj.__dict__.get(self.__name__)
        if _thread is None:
            _thread = Thread(target=self.func, args=(obj,))
            # thread.daemon causes the thread to terminate when the main
            # process ends
            _thread.daemon = True
            obj.__dict__[self.__name__] = _thread
        return _thread


def wait_dir(path):
    """Wait until the `path` folder creation."""
    while True:
        if os.path.exists(path) and os.path.isdir(path):
            break
        time.sleep(5)


class AsyncFileNotifier(object):
    def __init__(self, paths, callback):
        class EventHandler(ProcessEvent):
            def process_IN_CREATE(self, event):
                callback()

            def process_IN_DELETE(self, event):
                callback()

        manager = WatchManager()  # Watch Manager
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
        self.async_notifier = AsyncNotifier(manager, EventHandler())
        # aggregate inotify events
        try:
            self.async_notifier.coalesce_events()
        except AttributeError as inst:
            LOG.warn('Can not coalesce events, pyinotify does not seem to '
                     'support it (maybe too old): %s' % inst)
        for path in paths:
            if os.path.exists(path):
                manager.add_watch(path, mask, rec=False)
            else:
                LOG.warn("%s folder doesn't exist yet." % path)
                wait_dir(path)
                manager.add_watch(path, mask, rec=False)
                LOG.info("%s has just been created." % path)

    def loop(self):
        LOG.info("Starting inotify daemon.")
        asyncore.loop()

# ***
# Modified generic daemon class
# ***

# Author:         http://www.jejik.com/articles/2007/02/
#                         a_simple_unix_linux_daemon_in_python/www.boxedice.com

# License:        http://creativecommons.org/licenses/by-sa/3.0/

# Changes:        23rd Jan 2009 (David Mytton <david@boxedice.com>)
#                 - Replaced hard coded '/dev/null in __init__ with os.devnull
#                 - Added OS check to conditionally remove code that doesn't
#                   work on OS X
#                 - Added output to console on completion
#                 - Tidied up formatting
#                 11th Mar 2009 (David Mytton <david@boxedice.com>)
#                 - Fixed problem with daemon exiting on Python 2.4
#                   (before SystemExit was part of the Exception base)
#                 13th Aug 2010 (David Mytton <david@boxedice.com>
#                 - Fixed unhandled exception if PID file is empty
# Core modules


class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, main, stdin=os.devnull,
                 stdout=os.devnull, stderr=os.devnull,
                 home_dir='.', umask=022):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.home_dir = home_dir
        self.umask = umask
        self.main = main
        self.daemon_alive = True

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write(
                "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write(
                "fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        if sys.platform != 'darwin':  # This block breaks on OS X
            # Redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            si = file(self.stdin, 'r')
            so = file(self.stdout, 'a+')
            if self.stderr:
                se = file(self.stderr, 'a+', 0)
            else:
                se = so
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

        def sigtermhandler(signum, frame):
            self.daemon_alive = False
            signal.signal(signal.SIGTERM, sigtermhandler)
            signal.signal(signal.SIGINT, sigtermhandler)

        # Write pidfile
        atexit.register(
            self.delpid)  # Make sure pid file is removed if we quit
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self, *args, **kwargs):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None

        if pid:
            message = "pidfile %s already exists. Is it already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run(*args, **kwargs)

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        self.main()
