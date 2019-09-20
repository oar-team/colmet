""" ZeroMQ (asynchronous distributed messaging) library used to send measurements from nodes to collector
    push/pull messaging pattern : https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pushpull.html
"""

import zmq
import logging
import socket
import msgpack


LOG = logging.getLogger()

try:
    _snd_hwm = zmq.HWM
    _rcv_hwm = zmq.HWM
except AttributeError:
    _snd_hwm = zmq.SNDHWM
    _rcv_hwm = zmq.RCVHWM



class ZMQInputBackend(object):
    """ Class used by collector to receive data
    """

    def __init__(self):
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)

    def open(self, linger, high_water_mark, bind_uri):
        self.receiver.setsockopt(zmq.LINGER, linger)
        self.receiver.setsockopt(_rcv_hwm, high_water_mark)
        LOG.debug("Use the bind URI '%s'" % bind_uri)
        self.receiver.bind(bind_uri)

    def close(self):
        self.receiver.close()
        self.context.term()

    def receive(self, buffer_size=1000):
        res = []
        while True:
            try:
                received_data = self.receiver.recv(zmq.NOBLOCK)
                received_data = msgpack.unpackb(received_data)
                res.append(received_data)
                del received_data
            except zmq.ZMQError as e:
                if e.errno != zmq.EAGAIN:
                    raise e
                else:  # zmq.EAGAIN is raised when there is no more message available in the queue
                    LOG.debug("Zeromq receive queue is currently empty")
                    return res


class ZMQOutputBackend(object):
    """ Class used by node to send data
    """

    def __init__(self):
        self.context = zmq.Context()
        self.hostname = socket.gethostname()
        self.socket = self.context.socket(zmq.PUSH)

    def open(self, linger, high_water_mark, bind_uri):
        self.socket.setsockopt(zmq.LINGER, linger)
        self.socket.setsockopt(_snd_hwm, high_water_mark)
        self.socket.connect(bind_uri)
        LOG.debug("Use the URI '%s'" % bind_uri)

    def close(self):
        self.socket.close()
        self.context.term()

    def send(self, data):
        print("sending measurements with zeromq")
        self.socket.send(data)
