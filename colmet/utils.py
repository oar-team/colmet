import os
import asyncore
import time
import pyinotify
from threading import Thread
from pyinotify import ProcessEvent, AsyncNotifier, WatchManager
import logging


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


class WaitDirNotifier(object):
    """Wait until the `path` folder creation."""
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def loop(self):
        if os.path.exists(self.path) and os.path.isdir(self.path):
            return

        def get_first_existent_parent(path):
            parent, _ = os.path.split(path)
            if os.path.exists(parent) and os.path.isdir(parent):
                return parent
            else:
                return get_first_existent_parent(parent)

        class EventHandler(ProcessEvent):
            def process_IN_CREATE(self, event):
                pass

        watched_dir = get_first_existent_parent(self.path)
        m = pyinotify.WatchManager()
        m.add_watch(watched_dir, pyinotify.IN_CREATE, rec=True)
        notifier = pyinotify.Notifier(m, EventHandler(), 0, 0, 10)

        while True:
            try:
                notifier.process_events()
                if notifier.check_events():
                    notifier.read_events()
                if os.path.exists(self.path) and os.path.isdir(self.path):
                    notifier.stop()
                    time.sleep(1)
                    break
            except:
                notifier.stop()
                break


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
        self.async_notifier.coalesce_events()
        for path in paths:
            if os.path.exists(path):
                manager.add_watch(path, mask, rec=False)
            else:
                LOG.warn("%s folder doesn't exist yet." % path)
                WaitDirNotifier(path).loop()
                manager.add_watch(path, mask, rec=False)
                LOG.info("%s has just been created." % path)

    def loop(self):
        LOG.info("Starting inotify daemon.")
        asyncore.loop()
