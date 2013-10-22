
from nose.tools import *

from colmet.importer import get_module
from colmet.exceptions import UnableToImportModuleError

@raises(UnableToImportModuleError)
def test_if_importer_fail_if_module_not_found():
    get_module('colmet.metrics','this_module_does_not_exist')

def test_if_importer_success_to_import_module():
    m=get_module('colmet.metrics','taskstats_default')
    assert(m.__name__ == "colmet.metrics.taskstats_default")

