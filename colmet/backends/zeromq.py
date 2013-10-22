'''
ZeroMQ input backend for colmet collector
'''

import zmq
import logging
import socket

LOG = logging.getLogger()

from colmet.metrics.base import BaseCounters

from colmet.backends.base import InputBaseBackend, OutputBaseBackend


def get_output_backend_class():
    return ZMQOutputBackend


def get_input_backend_class():
    return ZMQInputBackend


class ZMQInputBackend(InputBaseBackend):
    @classmethod
    def _get_backend_name(cls):
        return "zeromq"

    def __init__(self, options):
        InputBaseBackend.__init__(self, options)

        self.context = zmq.Context()

        self.zeromq_bind_uri = options.zeromq_bind_uri

        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, "")
        LOG.debug("Use the bind URI '%s'" % self.zeromq_bind_uri)
        self.socket.bind(self.zeromq_bind_uri)

    def pull(self):
        raw = self.socket.recv(copy=False)
        LOG.debug("raw length %s" % len(raw.bytes))
        counters_list = BaseCounters.unpack_to_list(raw.bytes)
        del raw
        LOG.debug("%s counters received" % len(counters_list))
        if self.job_id_list is not None:
            counters_list = [metric for metric in counters_list
                             if metric.job_id in self.job_id_list]
            LOG.debug("%s counters received after filtering"
                      % len(counters_list))
        return counters_list


class ZMQOutputBackend(OutputBaseBackend):
    '''
    zmq node backend class
    '''

    @classmethod
    def _get_backend_name(cls):
        return "zeromq"

    def __init__(self, options):
        OutputBaseBackend.__init__(self, options)

        self.context = zmq.Context()
        self.hostname = socket.gethostname()

        self.zeromq_uri = options.zeromq_uri

        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect(self.zeromq_uri)
        LOG.debug("Use the URI '%s'" % self.zeromq_uri)

    def push(self, counters_list):
        '''
        push the metrics to the output backend
        '''

#        if counters_list.__class__.__name__ == 'list':
#            counters_ll = counters_list
#        else:
#            counters_ll = [counters_list]
#
#        for counters_lst in counters_ll:

        if len(counters_list) > 0:
            raw = BaseCounters.pack_from_list(counters_list)
            self.socket.send(raw)
#
#
#        if counters_list.__class__.__name__ == 'list':
#            raw = BaseCounters.pack_from_list(counters_list)
#            self.socket.send(raw)
#        else:
#
#            if len(counters_list) > 0:
#                raw = BaseCounters.pack_from_list(counters_list)
#                self.socket.send(raw)
#
