import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)  # noqa
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__,
                                                      prefix=__name__ + '.'):
        __import__(modname)

from colmet.common.exceptions import UnableToFindCounterClassError
from .base import BaseCounters


def find_inheritors_counters(klass):
    subclasses = {}
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses[child.__metric_name__] = child
                work.append(child)
    return subclasses

counters_registry = find_inheritors_counters(BaseCounters)


def get_counters_class(metric):
    if metric in counters_registry:
        return counters_registry[metric]
    raise UnableToFindCounterClassError(metric)
