class BaseBackend(object):

    def __init__(self, options):
        self.options = options

    def open(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def get_backend_name(self):
        return self.__backend_name__


class OutputBaseBackend(BaseBackend):

    def __init__(self, options):
        super(OutputBaseBackend, self).__init__(options)

    def push(self, msg):
        raise NotImplementedError()


class InputBaseBackend(BaseBackend):

    def __init__(self, options):
        super(InputBaseBackend, self).__init__(options)
        self.job_id_list = []

    def pull(self, request, timestamp):
        raise NotImplementedError()

    def get_counters_class(self, timestamp):
        raise NotImplementedError()


class StdoutBackend(OutputBaseBackend):
    '''
    stdout backend class
    '''
    __backend_name__ = "stdout"

    def open(self):
        pass

    def close(self):
        pass

    def push(self, counters_list):
        '''
        put the metrics to the output backend
        '''
        for counters in counters_list:
            print(counters)
