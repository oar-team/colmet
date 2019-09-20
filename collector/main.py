import collections
import logging
import time
from zeromq import ZMQInputBackend
from args_parser import ArgsParser
from counter import CounterFactory
from elasticsearch import ElasticsearchOutputBackend


def main():
    args = ArgsParser.get_args()

    # configure the root logger
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=40 - args.verbosity * 10)  # set logging level, always display CRITICAL (50) and ERROR (40)

    zeromq = ZMQInputBackend()
    zeromq.open(args.zeromq_linger, args.zeromq_hwm, "tcp://0.0.0.0:5556")
    stdout_backend = StdoutBackend()

    if args.elastic_host:
        elasticsearch_backend = ElasticsearchOutputBackend(args.elastic_host)

    while True:
        received_data = zeromq.receive()
        stdout_backend.push(received_data)
        if received_data:
            if args.elastic_host:
                elasticsearch_backend.push(CounterFactory(received_data).get_counters())
        sleep(args.sampling_period)


def sleep(duration):
    now = time.time()
    time_to_wait = ((now // duration) + 1) * duration - now
    # time.sleep(time_to_wait)
    time.sleep(1)


class StdoutBackend():

    def __init__(self):
        pass

    @staticmethod
    def push(measurements):
        if measurements:
            counters = CounterFactory(measurements).get_counters()
            for counter in counters:
                print("\n", "Timestamp :", counter.timestamp, " / Job :", counter.job_id, " / Hostname :", counter.hostname ,  "/ Backend :", counter.backend_name)
                for metric_name, metric_value in counter.metrics.items():
                    print('{:>25} : {}'.format(metric_name, str(metric_value)))


if __name__ == '__main__':
    main()