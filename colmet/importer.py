
import logging
import sys
import traceback

LOG = logging.getLogger()

from colmet.exceptions import UnableToImportModuleError


def get_module(modulebasepath, modulename):

    modulepath = "%s.%s" % (modulebasepath, modulename)
    try:
        module = __import__(
            modulepath,
            fromlist=[modulebasepath]
        )
    except ImportError, e:
        LOG.debug(e)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        LOG.debug(traceback.format_exc(exc_traceback))
        raise UnableToImportModuleError(modulepath, e)

    return module
