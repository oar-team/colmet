"""Colmet-node User Interface"""

from __future__ import print_function
import logging
import argparse
import signal
import sys
import copy
import time

from colmet import VERSION
from colmet.common.backends.zeromq import ZMQInputBackend
from colmet.common.backends.base import StdoutBackend
from colmet.common.exceptions import Error, NoneValueError


LOG = logging.getLogger()


class Task(object):

    def __init__(self, name, options):
        self.name = name
        self.options = options
        self.output_backends = []
        self.init_output_backends()
        self.input_backend = ZMQInputBackend(self.options)
        self.counters_list = []
        self.buffer_size = self.options.buffer_size

    def init_output_backends(self):
        for backend in self.output_backends:
            backend.close()
            del backend
        self.output_backends[:] = []
        options = copy.deepcopy(self.options)
        if options.hdf5_filepath is not None:
            if not options.hdf5_filepath.endswith(".hdf5"):
                options.hdf5_filepath = "%s.%s.hdf5" % \
                    (options.hdf5_filepath, int(time.time()))
            from colmet.collector.hdf5 import HDF5OutputBackend
            self.output_backends.append(HDF5OutputBackend(options))
        if self.options.enable_stdout_backend:
            self.output_backends.append(StdoutBackend(options))
        if self.options.elastic_host is not None:
            from colmet.collector.elasticsearch import ElasticsearchOutputBackend
            self.output_backends.append(ElasticsearchOutputBackend(options))
        for backend in self.output_backends:
            backend.open()

    def start(self):
        LOG.info("Starting %s" % self.name)
        self.input_backend.open()
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)
        signal.signal(signal.SIGHUP, self.reload)
        try:
            self.loop()
        except:
            self.close_backends()
            raise

    def push(self):
        for backend in self.output_backends:
            if len(self.counters_list) > 0:
                try:
                    backend.push(self.counters_list)
                    LOG.debug("%s metrics has been pushed with %s"
                          % (len(self.counters_list),
                             backend.get_backend_name()))
                except (NoneValueError, TypeError):
                    LOG.debug("Values for metrics are not there.")
        del self.counters_list[:]

    def close_backends(self):
        self.input_backend.close()
        self.push()
        for backend in self.output_backends:
            backend.close()

    def terminate(self, *args, **kwargs):
        LOG.info("Terminating %s" % self.name)
        self.close_backends()
        sys.exit(0)

    def reload(self, *args, **kwargs):
        LOG.info("Reloading %s" % self.name)
        self.push()
        self.init_output_backends()

    def sleep(self):
        # absolute time is used and based on seconds since 1970-01-01 00:00:00
        # UTC
        now = time.time()
        time_towait = (((now // self.options.sampling_period) + 1) *
                       self.options.sampling_period - now)
        time.sleep(time_towait)

    def loop(self):
        while True:
            now = time.time()
            LOG.debug("Gathering the metrics")
            self.counters_list = \
                self.input_backend.pull(self.options.buffer_size)

            LOG.debug("%s metrics has been pulled from zeromq" %
                      len(self.counters_list))

            LOG.debug("time to take measure: %s sec" % (time.time() - now))

            self.push()
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

    group = parser.add_argument_group('Elasticsearch')

    group.add_argument("--elastic-host", dest='elastic_host', default=None,
                       help="The address of Elasticsearch server, ex:'localhost:9200'")

    group.add_argument("--elastic-index-prefix", dest='elastic_index_prefix', default="colmet_",
                       help="Prefix for indices into elastisearch, ex:'colmet_dahu_'")

    args = parser.parse_args()

    if args.hdf5_filepath is None and args.enable_stdout_backend is False and args.elastic_host is None:
        parser.error("You need to provide at least one output backend "
                     "[hdf5|stdout|elasticsearch]")

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
