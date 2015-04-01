'''
Colmet-node User Interface
'''
import logging
import argparse
import signal
import sys
import time

from colmet import VERSION
from colmet.node.backends.procstats import ProcstatsBackend
from colmet.node.backends.taskstats import TaskstatsBackend
from colmet.common.backends.zeromq import ZMQOutputBackend
from colmet.common.utils import AsyncFileNotifier, as_thread
from colmet.common.exceptions import Error, NoneValueError


LOG = logging.getLogger()


class Task(object):

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.input_backends = []
        self.taskstats_backend = TaskstatsBackend(self.options)
        self.input_backends.append(self.taskstats_backend)
        if not self.options.disable_procstats:
            self.input_backends.append(ProcstatsBackend(self.options))
        self.zeromq_output_backend = ZMQOutputBackend(self.options)

    @as_thread
    def check_jobs_thread(self):
        notifier = \
            AsyncFileNotifier(paths=self.options.cpuset_rootpath,
                              callback=self.taskstats_backend.update_job_list)
        # Initial job list update
        self.update_job_list()
        notifier.loop()

    def update_job_list(self):
        self.taskstats_backend.update_job_list()

    def start(self):
        LOG.info("Starting %s" % self.name)
        for backend in self.input_backends:
            backend.open()
        self.zeromq_output_backend.open()
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        self.check_jobs_thread.start()
        self.loop()

    def terminate(self, signum, frame):
        LOG.info("Received a signal (%d)" % signum)
        LOG.info("Terminating %s properly..." % self.name)
        self.zeromq_output_backend.close()
        sys.exit(0)

    def sleep(self):
        now = time.time()
        time_towait = (((now // self.options.sampling_period) + 1) *
                       self.options.sampling_period - now)
        time.sleep(time_towait)

    def loop(self):
        while True:
            now = time.time()
            LOG.debug("Gathering the metrics")
            counters_list = []
            for backend in self.input_backends:
                pulled_counters = backend.pull()

                if backend.get_backend_name() == 'taskstats':
                    if len(pulled_counters) > 0:
                        for counters in pulled_counters:
                            counters_list += counters
                else:
                    counters_list += pulled_counters

                LOG.debug("%s metrics has been pulled width %s" %
                          (len(pulled_counters), backend.get_backend_name()))

            LOG.debug("time to take measure: %s sec" % (time.time() - now))

            if len(counters_list) > 0:
                # print "nb counters_list", len(counters_list)
                try:
                    self.zeromq_output_backend.push(counters_list)
                    LOG.debug("%s metrics has been pushed with zeromq"
                              % (len(counters_list)))
                except (NoneValueError, TypeError):
                    LOG.debug("Values for metrics are not there.")
            # sleep to next sampling
            self.sleep()


#
# Main program
#

DESCRIPTION = '''Display and/or collect cpu, memory and i/o bandwidth used
by the processes in a cpuset or a cgroup.'''


def main():
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=formatter)

    parser.add_argument('--version', action='version',
                        version='colmet version %s' % VERSION)

    parser.add_argument('-v', '--verbose', action='count', dest="verbosity",
                        default=1)

    parser.add_argument('-s', '--sample-period', type=float,
                        dest='sampling_period', default=5,
                        help='Sampling period of measuring in seconds')

    parser.add_argument('--disable-procstats', action="store_true",
                        default=False, dest="disable_procstats",
                        help='Disables node monitoring based on some /proc '
                             'subdirectories contents. Measures are '
                             'associated to the fictive job with 0 as '
                             'identifier (job_id)')

    group = parser.add_argument_group('Taskstat')

    group.add_argument('-c', '--cgroup', dest='cgroups',
                       action='append', default=[],
                       help='cgroup/cpuset to monitor', metavar='CGROUP')
    group.add_argument('-p', '--pid', type=int, dest='pids',
                       action='append', default=[],
                       help='process id to monitor', metavar='PID')
    group.add_argument('-t', '--tid', type=int, dest='tids',
                       action='append', default=[],
                       help='task ids to monitor', metavar='TID')
    group.add_argument('--cpuset_rootpath', dest='cpuset_rootpath',
                       action='append', default=["/dev/oar_cgroups/oar/"],
                       help='cpuset root path', metavar='CPUSETROOTPATH')
    group.add_argument('--regex_job_id', dest='regex_job_id',
                       action='append', default=['_(\d+)$'],
                       metavar='REGEXJOBID',
                       help='regular expression to extract job_id from '
                            'cpuset directory name', )
    parser.add_argument_group(group)

    group = parser.add_argument_group('Zeromq')

    group.add_argument("--zeromq-uri", dest='zeromq_uri',
                       help="ZeroMQ collector URI",
                       default='tcp://127.0.0.1:5556')

    group.add_argument("--zeromq-hwm", type=int,
                       default=1000, dest='zeromq_hwm',
                       help="The high water mark is a hard limit on the"
                            " maximum number of outstanding messages "
                            " ZeroMQ shall queue in memory. The value "
                            " of zero means \"no limit\".")

    group.add_argument("--zeromq-linger", type=int,
                       default=0, dest='zeromq_linger',
                       help="Set the linger period for the specified socket."
                            " The value of -1 specifies an infinite linger"
                            " period. The value of 0 specifies no linger"
                            " period.  Positive values specify an upper bound"
                            " for the  linger period in milliseconds.")

    parser.add_argument_group(group)

    args = parser.parse_args()

    # Set the logging value (always display CRITICAL and ERROR)
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=40 - args.verbosity * 10,
    )

    # run
    try:
        Task(sys.argv[0], args).start()
    except KeyboardInterrupt:
        pass
    except Error as err:
        err.show()
        sys.exit(1)
    except Exception as err:
        msg = "Error not handled '%s'" % err.__class__.__name__
        logging.critical(msg)
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            print(repr(err))
        raise


if __name__ == '__main__':
    main()
