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

config = {"perfhw_metrics": sys.argv[2], "sample_period": sys.argv[1]}

print("config", config)

sender.send(msgpack.packb(config))
