'''
stdout backend : print information to stdout
'''


from colmet.backends.base import OutputBaseBackend


def get_output_backend_class():
    return Backend


class Backend(OutputBaseBackend):
    '''
    stdout backend class
    '''
    @classmethod
    def _get_backend_name(cls):
        return "stdout"

    def __init__(self, options):
        super(Backend, self).__init__(options)

    def push(self, counters_list):
        '''
        put the metrics to the output backend
        '''
        for counters in counters_list:
            print counters
