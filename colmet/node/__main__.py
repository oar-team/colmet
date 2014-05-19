'''
Colmet-node User Interface
'''
import logging
import optparse
import signal
import sys
import time

from colmet import VERSION
from colmet.node.backends.procstats import ProcstatsBackend
from colmet.node.backends.taskstats import TaskstatsBackend
from colmet.common.backends.zeromq import ZMQOutputBackend
from colmet.common.utils import AsyncFileNotifier, as_thread
from colmet.common.utils import Daemon, optparse_add_default_value
from colmet.common.exceptions import Error, NoneValueError


LOG = logging.getLogger()


class Task(object):

    def __init__(self, options):
        self.options = options
        self.taskstats_backend = TaskstatsBackend(self.options)
        self.procstats_backend = ProcstatsBackend(self.options)
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
        LOG.info("Starting Colmet-node")
        self.taskstats_backend.open()
        self.procstats_backend.open()
        self.zeromq_output_backend.open()
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        self.check_jobs_thread.start()
        self.loop()

    def terminate(self, *args, **kwargs):
        LOG.info("Terminating Colmet-node")
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
            for backend in [self.taskstats_backend, self.procstats_backend]:
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
                #print "nb counters_list", len(counters_list)
                try:
                    self.zeromq_output_backend.push(counters_list)
                    LOG.debug("%s metrics has been pushed with zeromq"
                              % (len(counters_list)))
                except (NoneValueError, TypeError):
                    LOG.debug("Values for metrics are not there.")
            # sleep to next sampling
            self.sleep()
        LOG.info("Ending Colmet")


#
# Main program
#

USAGE = '''%s [OPTIONS]

Collect cpu, memory and i/o bandwidth used by the processes in a cpuset or a
cgroup and send metrics from zeromq''' % sys.argv[0]


def main():
    parser = optparse.OptionParser(usage=USAGE, version='colmet ' + VERSION)

    parser.add_option('-v', '--verbose', action='count', dest="verbosity",
                      default=0)

    parser.add_option('-s', '--sample-period', type='float',
                      dest='sampling_period', metavar='SEC', default=5,
                      help='sampling period of measuring [5 second]')

    parser.add_option('--daemon', dest='run_as_daemon',
                      help='Run as daemon [False]',
                      action='store_true', default=False)

    parser.add_option('--pidfile', dest='pidfile', type="str",
                      default="/var/run/colmet.pid",
                      help='pid file when running as daemon [/var/run/colmet.pid]')

    parser.add_option('--logfile', dest='logfile', type="str",
                      default="/var/log/colmet.log",
                      help='pid file when running as daemon [/var/log/colmet.log]')

    group = optparse.OptionGroup(parser, "Taskstat")

    group.add_option('-c', '--cgroup', type='str', dest='cgroups',
                     action='append', default=[],
                     help='cgroup/cpuset to monitor', metavar='CGROUP')
    group.add_option('-p', '--pid', type='int', dest='pids',
                     action='append', default=[],
                     help='process id to monitor', metavar='PID')
    group.add_option('-t', '--tid', type='int', dest='tids',
                     action='append', default=[],
                     help='task ids to monitor', metavar='TID')
    group.add_option('--cpuset_rootpath', type='str', dest='cpuset_rootpath',
                     action='append', default=["/dev/oar_cgroups/oar/"],
                     help='cpuset root path', metavar='CPUSETROOTPATH')
    group.add_option('--regex_job_id', type='str', dest='regex_job_id',
                     action='append', default=['_(\d+)$'],
                     metavar='REGEXJOBID',
                     help='regular expression to extract job_id from '
                          'cpuset directory name', )
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Zeromq")
    group.add_option("--zeromq-uri", type='str',
                     dest='zeromq_uri', default='tcp://127.0.0.1:5556')
    group.add_option("--zeromq-hwm", type='int', dest='zeromq_hwm',
                     default=1000,
                     help="The high water mark is a hard limit on the maximum"
                          " number of outstanding messages ZeroMQ shall queue"
                          " in memory. The value of zero means \"no limit\".")
    group.add_option("--zeromq-swap", type='int', dest='zeromq_swap',
                     default=(200 * 2 ** 10),
                     help="Defines the maximum size of the swap space in"
                          " bytes. ZeroMQ will use a this local swapfile to"
                          " store messages that exceed the high water mark.")
    group.add_option("--zeromq-linger", type='int',
                     default=0, dest='zeromq_linger',
                     help="Set the linger period for the specified socket."
                          " The value of -1 specifies an infinite linger"
                          " period. The value of 0 specifies no linger period."
                          " Positive values specify an upper bound for the "
                          " linger period in milliseconds.")

    parser.add_option_group(group)

    optparse_add_default_value(parser)

    options, args = parser.parse_args()
    if args:
        parser.error('Unexpected arguments: ' + ' '.join(args))

    # Set the logging value (always display CRITICAL and ERROR)
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=40 - options.verbosity * 10,
    )

    # run
    main_loop = lambda: Task(options).start()
    try:
        if not options.run_as_daemon:
            main_loop()
        else:
            daemon = Daemon(options.pidfile, main_loop, stderr=options.logfile)
            daemon.start()
    except KeyboardInterrupt:
        pass
    except Error as err:
        err.show()
        sys.exit(1)
    except Exception as err:
        MSG = "Error not handled '%s'" % err.__class__.__name__
        logging.critical(MSG)
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            print repr(err)
        raise


if __name__ == '__main__':
    main()
