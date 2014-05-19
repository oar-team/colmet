'''
Colmet-node User Interface
'''
import logging
import optparse
import signal
import sys
import time

from colmet import VERSION
from colmet.hdf5_collector.hdf5 import HDF5OutputBackend
from colmet.common.backends.zeromq import ZMQInputBackend
from colmet.common.utils import Daemon, optparse_add_default_value
from colmet.common.exceptions import Error, NoneValueError


LOG = logging.getLogger()


class Task(object):

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.hdf5_output_backend = HDF5OutputBackend(self.options)
        self.zeromq_input_backend = ZMQInputBackend(self.options)

    def start(self):
        LOG.info("Starting %s" % self.name)
        self.hdf5_output_backend.open()
        self.zeromq_input_backend.open()
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        self.loop()

    def terminate(self, *args, **kwargs):
        LOG.info("Terminating %s" % self.name)
        self.zeromq_input_backend.close()
        sys.exit(0)

    def sleep(self):
        #absolute time is used and based on seconds since 1970-01-01 00:00:00 UTC
        now = time.time()
        time_towait = (((now // self.options.sampling_period) + 1) *
                       self.options.sampling_period - now)
        time.sleep(time_towait)

    def loop(self):
        while True:
            now = time.time()
            LOG.debug("Gathering the metrics")
            pulled_counters = self.zeromq_input_backend.pull()

            LOG.debug("%s metrics has been pulled from zeromq" %
                      len(pulled_counters))

            LOG.debug("time to take measure: %s sec" % (time.time() - now))

            if len(pulled_counters) > 0:
                try:
                    self.hdf5_output_backend.push(pulled_counters)
                    LOG.debug("%s metrics has been pushed to hdf5"
                              % (len(pulled_counters)))
                except (NoneValueError, TypeError):
                    LOG.debug("Values for metrics are not there.")
            # sleep to next sampling
            self.sleep()
        LOG.info("Ending Colmet")


#
# Main program
#

USAGE = '''%s [OPTIONS]

Display and/or collect cpu, memory and i/o bandwidth used by the processes in a
cpuset or a cgroup.''' % sys.argv[0]


def main():
    parser = optparse.OptionParser(usage=USAGE, version='colmet ' + VERSION)

    parser.add_option('-s', '--sample-period', type='float',
                      metavar='SEC', default=5, dest='sampling_period',
                      help='sampling period of measuring in seconds.')

    parser.add_option('--daemon', dest='run_as_daemon',
                      help='Run as daemon [False]',
                      action='store_true', default=False)
    parser.add_option('--pidfile', dest='pidfile', type="str",
                      help='pid file when running as daemon.',
                      default="/var/run/colmet.pid")

    parser.add_option('--logfile', dest='logfile', type="str",
                      help='pid file when running as daemon.',
                      default="/var/log/colmet.log")

    parser.add_option('-v', '--verbose', action='count', dest="verbosity",
                      default=0)

    group = optparse.OptionGroup(parser, "Zeromq")
    group.add_option("--zeromq-bind-uri", type='str',
                     dest='zeromq_bind_uri', default='tcp://0.0.0.0:5556')

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

    group = optparse.OptionGroup(parser, "HDF5")
    group.add_option("--hdf5-filepath", type='str',
                     help='The file path used to store the hdf5 data',
                     dest='hdf5_filepath', default='/tmp/colmet/hdf5/counters.hdf5')

    group.add_option("--hdf5-complevel", type=int,
                     help='Specifies a compression level for data. '
                          'The allowed range is 0-9. A value of 0 '
                          '(the default) disables compression.',
                     dest='hdf5_complevel', default=0)

    group.add_option("--hdf5-complib", type='str',
                     help='Specifies the compression library to be used. '
                          '"zlib" (the default), "lzo", "bzip2" and "blosc" '
                          'are supported.',
                     dest='hdf5_complib', default='zlib')

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
    main_loop = lambda: Task("Colmet HDF5 Collector", options).start()
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
