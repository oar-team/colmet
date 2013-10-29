
from threading import Thread


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
