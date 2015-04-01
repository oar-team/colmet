import asyncore
import logging
import os
from threading import Thread
import time

from pyinotify import ProcessEvent, AsyncNotifier, WatchManager
import pyinotify

LOG = logging.getLogger()


class ThreadProperty(object):
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


as_thread = ThreadProperty


def wait_dir(path):
    """Wait until the `path` folder creation."""
    while True:
        if os.path.exists(path) and os.path.isdir(path):
            break
        time.sleep(5)


class AsyncFileNotifier(object):
    def __init__(self, paths, callback):
        class EventHandler(ProcessEvent):
            def process_IN_CREATE(self, event):  # noqa
                callback()

            def process_IN_DELETE(self, event):  # noqa
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
