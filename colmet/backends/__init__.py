
import pkgutil

from colmet.importer import get_module
from colmet.exceptions import BackendNotFoundInModule


def get_input_backend_class(backend_name):
    module = get_module("colmet.backends", backend_name)
    try:
        return module.get_input_backend_class()
    except:
        raise BackendNotFoundInModule('Input', backend_name)


def get_output_backend_class(backend_name):
    module = get_module("colmet.backends", backend_name)
    try:
        return module.get_output_backend_class()
    except:
        raise BackendNotFoundInModule('Output', backend_name)


def get_input_backend_list():
    backends = list()

    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        try:
            get_input_backend_class(modname)
        except Exception:
            pass
        else:
            backends.append(modname)

    return backends


def get_output_backend_list():
    backends = list()

    for importer, modname, ispkg in pkgutil.iter_modules(__path__):
        try:
            get_output_backend_class(modname)
        except Exception:
            pass
        else:
            backends.append(modname)

    return backends
