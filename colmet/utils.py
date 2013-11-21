
import asyncore
import pyinotify
from threading import Thread
from pyinotify import ProcessEvent, AsyncNotifier, WatchManager


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


class AsyncFileNotifier(object):
    def __init__(self, paths, callback):
        class EventHandler(ProcessEvent):
            def process_IN_CREATE(self, event):
                callback()

            def process_IN_DELETE(self, event):
                callback()

        manager = WatchManager()  # Watch Manager
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
        AsyncNotifier(manager, EventHandler())
        for path in paths:
            manager.add_watch(path, mask, rec=False)

    def loop(self):
        asyncore.loop()
