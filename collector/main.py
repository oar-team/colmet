import collections
import logging
import time
from zeromq import ZMQInputBackend
from args_parser import ArgsParser


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

METRIC_NAMES_MAP = {1: "cache",
                    2: "rss",
                    3: "rss_huge",
                    4: "shmem",
                    5: "mapped_file",
                    6: "dirty",
                    7: "writeback",
                    8: "pgpgin",
                    9: "pgpgout",
                    10: "pgfault",
                    11: "pgmajfault",
                    12: "inactive_anon",
                    13: "active_anon",
                    14: "inactive_file",
                    15: "active_file",
                    16: "unevictable",
                    17: "hierarchical_memory_limit",
                    18: "total_cache",
                    19: "total_rss",
                    20: "total_rss_huge",
                    21: "total_shmem",
                    22: "total_mapped_file",
                    23: "total_dirty",
                    24: "total_writeback",
                    25: "total_pgpgin",
                    26: "total_pgpgout",
                    27: "total_pgfault",
                    28: "total_pgmajfault",
                    29: "total_inactive_anon",
                    30: "total_active_anon",
                    31: "total_inactive_file",
                    32: "total_active_file",
                    33: "total_unevictable",
                    34: "nr_periods", # Cpu Backend
                    35: "nr_throttled",
                    36: "throttled_time",
                    }


class StdoutBackend():

    @staticmethod
    def push(measurements):
        if measurements:
            measurements = measurements[0]
            for job_id, job_measurements in measurements.items():
                for backend_measurement in job_measurements[2]:
                    print("\n", "Time :", job_measurements[1], " / Job :", job_id, " / Backend :", str(backend_measurement[0]))
                    metric_names = []
                    for compressed_metric__name in backend_measurement[1]:
                        metric_names.append(METRIC_NAMES_MAP[compressed_metric__name])
                    metrics = dict(zip(metric_names, backend_measurement[2]))
                    # pprint.pprint(metrics, compact=False)
                    for metric_name, metric_value in metrics.items():
                        print('{:>25} : {}'.format(metric_name, str(metric_value)))


if __name__ == '__main__':
    main()