'''
Colmet Exceptions
'''
import logging
import sys
import traceback

LOG = logging.getLogger()


class Error(Exception):
    '''
    Generic error
    '''
    desc = "Generic Error"

    def __init__(self, desc_args={}):
        super(Error, self).__init__()
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        self.desc_args = desc_args

    def format(self):
        """
        Return the formatted error
        """
        msg = self.desc % self.desc_args
        if LOG.getEffectiveLevel() <= logging.DEBUG:
            msg += "\n\n" + traceback.format_exc(self.exc_traceback)
        return msg

    def show(self):
        '''
        Display the formatted error
        '''
        LOG.error(self.format())


class NoJobFoundError(Error):
    '''
    No Job Found Error
    '''
    desc = (
        "No job found/specified. "
        "You probably need to provide information "
        "about job to monitor on the command line."
    )


class NoEnoughPrivilegeError(Error):
    '''
    No Enough Privileges Error
    '''
    desc = (
        "No enough privileges to run this program. "
        "You probably need to be root."
    )


class UnableToFindCounterClassError(Error):
    '''
    Unable to find a counter class Error
    '''
    desc = (
        "An error occurs when importing the class %s:"
    )

    def format(self):
        msg = Error.format(self)
        if self.error is not None:
            msg += "\n" + str(self.error)
        return msg

    def __init__(self, class_name, error=None):
        Error.__init__(self)
        self.desc_args = class_name
        self.error = error


class CounterAlreadyExistError(Error):
    '''
    The counter Already Exist Error
    '''
    desc = (
        "A counter has been registered twice. "
        "This shouldn't append. Please contact the developpers."
    )


class JobNeedToBeDefinedError(Error):
    '''
    The monitored job id must be defined Error
    '''
    desc = (
        "Unable to find jobs in this node. "
        "Please check Taskstat options ('-h')."
    )


class UnableToFindLibraryError(Error):
    '''
    Unable to find library error
    '''
    desc = (
        "Unable to load the library '%s'. "
        "\nPlease check that your environnement provide it."
    )


class MultipleBackendsNotSupported(Error):
    '''
    Colmet doesn't support multiple input/output backend in the same process
    '''
    desc = (
        "Colmet doesn't support multiple "
        "input/output backend in the same process."
    )


class NotEnoughInputBackend(Error):
    desc = (
        "You need to provide at least one input backend "
        "on the command line"
    )


class FileAlreadyOpenWithDifferentModeError(Error):
    desc = (
        "The file %s is already opened with a different "
        "filemode access in the same process. This is "
        "not supported."
    )


class TimeoutException(Exception):
    '''
    A simple class to handle timeout for the main colmet loop
    '''
    pass


class NoneValueError(Error):
    '''
    Unable to retreive value for this metric
    '''
    pass


class VoidCpusetError(Error):
    '''
    This Cpuset is void
    '''
    pass
