import argparse

DESCRIPTION = "Display and/or collect cpu, memory and i/o bandwidth used by the processes in a cpuset or a cgroup."
VERSION = "2.0"


class ArgsParser(object):

    @staticmethod
    def get_args():
        formatter = argparse.ArgumentDefaultsHelpFormatter
        parser = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=formatter)

        parser.add_argument('--version', action='version', version='colmet version %s' % VERSION)

        parser.add_argument('-v', '--verbose', action='count', dest="verbosity", default=1)

        parser.add_argument('-s', '--sample-period', type=float, dest='sampling_period', default=5,
                            help='Sampling period of measuring in seconds')

        group = parser.add_argument_group('Zeromq')

        group.add_argument("--zeromq-uri", dest='zeromq_uri', default='tcp://0.0.0.0:5556',
                           help="ZeroMQ collector URI")

        group.add_argument("--zeromq-hwm", type=int, default=1000, dest='zeromq_hwm',
                           help="The high water mark is a hard limit on the maximum number of outstanding messages"
                                " ZeroMQ shall queue in memory. The value of zero means \"no limit\".")

        group.add_argument("--zeromq-linger", type=int, default=0, dest='zeromq_linger',
                           help="Set the linger period for the specified socket."
                                " The value of -1 specifies an infinite linger period. "
                                " The value of 0 specifies no linger period."
                                " Positive values specify an upper bound for the  linger period in milliseconds.")

        parser.add_argument_group(group)

        group = parser.add_argument_group('Elasticsearch')

        group.add_argument("--elastic-host", dest='elastic_host', default=None,
                           help="The address of Elasticsearch server, ex:'http://localhost:9200'")

        args = parser.parse_args()
        return args
