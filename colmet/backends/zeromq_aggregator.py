'''
ZeroMQ input backend for colmet collector
'''

import zmq
import logging
import socket

LOG = logging.getLogger()

from colmet.exceptions import JobNeedToBeDefinedError
from colmet.metrics.base import BaseCounters

from colmet.backends.base import InputBaseBackend, OutputBaseBackend


def get_output_backend_class():
    return ZMQOutputBackend


def get_input_backend_class():
    return ZMQInputBackend


class ZMQInputBackend(InputBaseBackend):
    @classmethod
    def _get_backend_name(cls):
        return "zeromq_aggregator"

    def __init__(self, options):
        InputBaseBackend.__init__(self, options)

        self.context = zmq.Context()

        self.zeromq_bind_uri = options.zeromq_bind_uri

        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, "")
        LOG.debug("Use the bind URI '%s'" % self.zeromq_bind_uri)
        self.socket.bind(self.zeromq_bind_uri)

    def pull(self):

        counters_list = []
        try:
            for i in xrange(1000):
                raw = self.socket.recv(zmq.NOBLOCK, copy=False)
                counters_list.extend(BaseCounters.unpack_to_list(raw.bytes))
                del raw
        except zmq.ZMQError, e:
            if e.errno != zmq.EAGAIN:
                raise e

        LOG.debug("%s counters received" % len(counters_list))
        if len(self.job_id_list) > 0:
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
        return "zeromq_aggregator"

    def __init__(self, options):
        OutputBaseBackend.__init__(self, options)

        self.context = zmq.Context()
        self.hostname = socket.gethostname()

        self.zeromq_uri = options.zeromq_uri

        if options.job_id is None:
            raise JobNeedToBeDefinedError()

        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect(self.zeromq_uri)
        LOG.debug("Use the URI '%s'" % self.zeromq_uri)

    def push(self, counters_list):
        '''
        push the metrics to the output backend
        '''

        if len(counters_list) > 0:
            msg = BaseCounters.pack_from_list(counters_list)
            self.socket.send(msg, 0)
