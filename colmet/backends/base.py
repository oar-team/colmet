

from colmet.exceptions import BackendMethodNotImplemented

class BaseBackend(object):
    def __init__(self, options):
        self.options = options

    @classmethod
    def _get_backend_name(cls):
        raise TypeError("You need to specify the name of your backend in _get_backend_name")

class OutputBaseBackend(BaseBackend):
    def __init__(self, options):
        BaseBackend.__init__(self, options)

    def push(self,msg):
        raise BackendMethodNotImplemented("push")

class InputBaseBackend(BaseBackend):
    def __init__(self, options):
        BaseBackend.__init__(self, options)

        self.job_id_list = list()
        self.job_id_list += options.job_id
        if options.job_min_id != None and options.job_max_id != None:
            self.job_id_list += range(options.job_min_id,options.job_max_id+1)


    def pull(self, request, timestamp):
        raise BackendMethodNotImplemented("pull")

    def get_counters_class(self, timestamp):
        raise BackendMethodNotImplemented("get_counters_class")


