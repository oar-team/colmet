'''
ZeroMQ input backend for colmet collector
'''

import zmq
import logging
import socket
import struct

LOG = logging.getLogger()

from colmet.common.metrics.base import BaseCounters

from colmet.common.backends.base import InputBaseBackend, OutputBaseBackend


class ZMQInputBackend(InputBaseBackend):
    __backend_name__ = "zeromq"

    def open(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.SUBSCRIBE, "")
        self.socket.setsockopt(zmq.LINGER, self.options.zeromq_linger)
        self.socket.setsockopt(zmq.HWM, self.options.zeromq_hwm)
        self.socket.setsockopt(zmq.SWAP, self.options.zeromq_swap)
        LOG.debug("Use the bind URI '%s'" % self.options.zeromq_bind_uri)
        self.socket.bind(self.options.zeromq_bind_uri)

    def close(self):
        self.socket.close()
        self.context.term()

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
    __backend_name__ = "zeromq"

    def open(self):
        self.context = zmq.Context()
        self.hostname = socket.gethostname()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.setsockopt(zmq.LINGER, self.options.zeromq_linger)
        self.socket.setsockopt(zmq.HWM, self.options.zeromq_hwm)
        self.socket.setsockopt(zmq.SWAP, self.options.zeromq_swap)
        self.socket.connect(self.options.zeromq_uri)
        LOG.debug("Use the URI '%s'" % self.options.zeromq_uri)

    def close(self):
        self.socket.close()
        self.context.term()

    def push(self, counters_list):
        '''
        push the metrics to the output backend
        '''
        if len(counters_list) > 0:
            try:
                raw = BaseCounters.pack_from_list(counters_list)
                self.socket.send(raw)
            except struct.error, e:
                LOG.error("An error occurred during packet creation : %s" % e)
