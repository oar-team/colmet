'''
ZeroMQ input backend for colmet collector
'''

import zmq
from zmq.eventloop import ioloop, zmqstream
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
        self.loop = ioloop.IOLoop.instance()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.setsockopt(zmq.LINGER, self.options.zeromq_linger)
        self.socket.setsockopt(zmq.HWM, self.options.zeromq_hwm)
        self.socket.setsockopt(zmq.SWAP, self.options.zeromq_swap)
        LOG.debug("Use the bind URI '%s'" % self.options.zeromq_bind_uri)
        self.socket.bind(self.options.zeromq_bind_uri)
        self.stream = zmqstream.ZMQStream(self.socket, self.loop)

    def close(self):
        self.socket.close()
        self.context.term()

    def unpack(self, msgs, callback):
        counters_list = []
        for raw in msgs:
            try:
                counters_list.extend(BaseCounters.unpack_to_list(raw))
            except Exception as e:
                LOG.exception(e)
        LOG.debug("%s counters received" % len(counters_list))
        for counters in counters_list:
            callback(counters)

    def on_recv(self, callback):
        intern_callback = lambda x: self.unpack(x, callback)
        self.stream.on_recv(intern_callback)


class ZMQOutputBackend(OutputBaseBackend):
    '''
    zmq node backend class
    '''
    __backend_name__ = "zeromq"

    def open(self):
        self.context = zmq.Context()
        self.hostname = socket.gethostname()
        self.socket = self.context.socket(zmq.PUSH)
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
