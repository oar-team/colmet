import zmq
import socket
import msgpack
from time import sleep
import sys

context = zmq.Context()
sender = context.socket(zmq.PUSH)

sender.setsockopt(zmq.LINGER, 0)
sender.setsockopt(zmq.SNDHWM, 1000)

sender.connect("tcp://127.0.0.1:5557")

print(float(sys.argv[1]))
sender.send(msgpack.packb(float(sys.argv[1])))