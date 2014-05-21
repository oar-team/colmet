'''
Colmet-node User Interface
'''
import logging
import argparse
import signal
import sys

from colmet import VERSION
from colmet.common.backends.zeromq import ZMQInputBackend
from colmet.common.backends.base import StdoutBackend
from colmet.common.utils import Daemon
from colmet.common.exceptions import Error, NoneValueError


LOG = logging.getLogger()


class Task(object):

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.output_backends = []
        if self.options.hdf5_filepath is not None:
            from colmet.collector.hdf5 import HDF5OutputBackend
            self.output_backends.append(HDF5OutputBackend(self.options))
        if self.options.enable_stdout_backend:
            self.output_backends.append(StdoutBackend(self.options))
        self.zeromq_input_backend = ZMQInputBackend(self.options)
        self.counters_list = []
        self.buffer_size = self.options.buffer_size

    def start(self):
        LOG.info("Starting %s" % self.name)
        for backend in self.output_backends:
            backend.open()
        self.zeromq_input_backend.open()
        self.zeromq_input_backend.on_recv(self.collect)
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        self.zeromq_input_backend.loop.start()

    def push(self):
        for backend in self.output_backends:
            try:
                backend.push(self.counters_list)
                LOG.info("%s new metrics has been pushed with %s"
                         % (len(self.counters_list),
                            backend.get_backend_name()))
            except (NoneValueError, TypeError):
                LOG.debug("Values for metrics are not there.")
        del self.counters_list[:]

    def collect(self, counter):
        self.counters_list.append(counter)
        if len(self.counters_list) >= self.options.buffer_size:
            self.push()

    def terminate(self, *args, **kwargs):
        LOG.info("Terminating %s" % self.name)
        self.zeromq_input_backend.loop.stop()
        self.zeromq_input_backend.close()
        self.push()
        for backend in self.output_backends:
            backend.close()
        sys.exit(0)


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

    parser.add_argument('--daemon', dest='run_as_daemon',
                        help='Runs as daemon',
                        action='store_true', default=False)

    parser.add_argument('--pidfile', dest='pidfile',
                        default="/var/run/colmet.pid",
                        help='Pid file used when running as daemon')

    parser.add_argument('--logfile', dest='logfile',
                        default="/var/log/colmet.log",
                        help='Logger file used when running as daemon')

    parser.add_argument('--buffer-size', dest='buffer_size', default=100,
                        help='Defines the maximum number of counters that '
                             'colmet should queue in memory before pushing '
                             'it to output backend', type=int)

    parser.add_argument("--enable-stdout-backend", action='store_true',
                        help='Prints the metrics on STDOUT',
                        dest='enable_stdout_backend', default=False)

    group = parser.add_argument_group('Zeromq')

    group.add_argument("--zeromq-bind-uri", dest='zeromq_bind_uri',
                       help="ZeroMQ bind URI",
                       default='tcp://0.0.0.0:5556')
    group.add_argument("--zeromq-hwm", type=int,
                       default=1000, dest='zeromq_hwm',
                       help="The high water mark is a hard limit on the"
                            " maximum number of outstanding messages "
                            " ZeroMQ shall queue in memory. The value "
                            " of zero means \"no limit\".")

    group.add_argument("--zeromq-swap", type=int, dest='zeromq_swap',
                       default=(200 * 2 ** 10),
                       help="Defines the maximum size of the swap space in"
                            " bytes. ZeroMQ will use a this local swapfile to"
                            " store messages that exceed the high water mark.")

    group.add_argument("--zeromq-linger", type=int,
                       default=0, dest='zeromq_linger',
                       help="Set the linger period for the specified socket."
                            " The value of -1 specifies an infinite linger"
                            " period. The value of 0 specifies no linger"
                            " period.  Positive values specify an upper bound"
                            " for the  linger period in milliseconds.")

    group = parser.add_argument_group('HDF5')

    group.add_argument("--hdf5-filepath", dest='hdf5_filepath', default=None,
                       help='The file path used to store the hdf5 data')

    group.add_argument("--hdf5-complevel", type=int, dest='hdf5_complevel',
                       help='Specifies a compression level for data. '
                            'The allowed range is 0-9. A value of 0 '
                            '(the default) disables compression.',
                       default=0)

    group.add_argument("--hdf5-complib", dest='hdf5_complib', default='zlib',
                       help='Specifies the compression library to be used. '
                            '"zlib" (the default), "lzo", "bzip2" and "blosc" '
                            'are supported.')

    args = parser.parse_args()

    if (args.hdf5_filepath is None and args.enable_stdout_backend is False):
        parser.error("You need to provide at least one output backend "
                     "[hdf5|stdout]")

    # Set the logging value (always display CRITICAL and ERROR)
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        level=40 - args.verbosity * 10,
    )

    # run
    main_loop = lambda: Task(sys.argv[0], args).start()
    try:
        if not args.run_as_daemon:
            main_loop()
        else:
            daemon = Daemon(args.pidfile, main_loop, stderr=args.logfile)
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
