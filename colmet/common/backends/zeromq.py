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

try:
    _snd_hwm = zmq.HWM
    _rcv_hwm = zmq.HWM
except AttributeError:
    _snd_hwm = zmq.SNDHWM
    _rcv_hwm = zmq.RCVHWM


class ZMQInputBackend(InputBaseBackend):
    __backend_name__ = "zeromq"

    def open(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.setsockopt(zmq.LINGER, self.options.zeromq_linger)
        self.socket.setsockopt(_rcv_hwm, self.options.zeromq_hwm)
        LOG.debug("Use the bind URI '%s'" % self.options.zeromq_bind_uri)
        self.socket.bind(self.options.zeromq_bind_uri)

    def close(self):
        self.socket.close()
        self.context.term()

    def pull(self, buffer_size=1000):
        counters_list = []
        try:
            for i in xrange(buffer_size):
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
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.setsockopt(zmq.LINGER, self.options.zeromq_linger)
        self.socket.setsockopt(_snd_hwm, self.options.zeromq_hwm)
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
            except struct.error as e:
                LOG.error("An error occurred during packet creation : %s" % e)
