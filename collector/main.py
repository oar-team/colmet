import collections
import logging
import time
from zeromq import ZMQInputBackend
from args_parser import ArgsParser
from metric import Metric, MetricFactory


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

    while True:
        received_data = zeromq.receive()
        stdout_backend.push(received_data)
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
            metrics = MetricFactory(measurements).get_metrics()
            for metric in metrics:
                print("\n", "Timestamp :", metric.timestamp, " / Job :", metric.job_id, " / Backend :", metric.backend_name)
                for metric_name, metric_value in metric.metrics.items():
                    print('{:>25} : {}'.format(metric_name, str(metric_value)))


if __name__ == '__main__':
    main()