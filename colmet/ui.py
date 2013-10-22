# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
# USA.
#
# See the COPYING file for license information.
#
#
# Copyright (c) 2012 Philippe Le Brouster <philippe.le-brouster@imag.fr>
'''
Colmet User Interface
'''
import locale
import optparse
import sys
import signal
import time
import errno
import logging

LOG = logging.getLogger()

from colmet import VERSION
from colmet.exceptions import Error, MultipleBackendsNotYetSupported, NotEnoughInputBackend, TimeoutException, NoneValueError
from colmet.backends import  get_input_backend_class, get_output_backend_class, get_input_backend_list, get_output_backend_list
from colmet.daemon import Daemon

class TaskMonBatch(object):

    def __init__(self, input_backends,output_backends,options):
        self.options = options
        self.input_backends = input_backends
        self.output_backends = output_backends

        signal.signal(signal.SIGUSR1, self.update_job_list)

    def timeout_handler(self, signum, frame):
        raise TimeoutException

    def update_job_list(self, signum, frame):
        LOG.debug("Catch signal %s, update job list to scan" % signum)
        for ib in self.input_backends:
          #print "ib_backend_name:", ib._get_backend_name()
          if ib._get_backend_name() == 'taskstats':
            #print "call update job list"
            ib.update_job_list()

    def run(self):
        iterations = 0
        if self.options.walltime != None:
            signal.signal(signal.SIGALRM,self.timeout_handler)
            signal.alarm(self.options.walltime)

        period = self.options.sampling_period

        while self.options.iterations is None or \
            iterations < self.options.iterations:

            #sleep to next sampling
            #absolute time is used and based on seconds since 1970-01-01 00:00:00 UTC
            now = time.time()
            time_towait = ((now // period) + 1) * period - now
            time.sleep(time_towait)

            now = time.time()
            LOG.debug("Gathering the metrics")
            counters_list = []
            for backend in self.input_backends:
                pulled_counters = backend.pull()

                if backend._get_backend_name() == 'taskstats':
                    if len(pulled_counters) > 0:
                        for counters in pulled_counters:
                            counters_list += counters
                else:
                    counters_list += pulled_counters

                LOG.debug("%s metrics has been pulled width %s" % (len(pulled_counters),backend._get_backend_name()))

            LOG.debug("time to take measure: %s sec" % (time.time()-now))

            for backend in self.output_backends:
                if len(counters_list) > 0:
                    #print "nb counters_list", len(counters_list)
                    try:
                        backend.push(counters_list)
                        LOG.debug("%s metrics has been pushed with %s" % (len(counters_list),backend._get_backend_name()))
                    except (NoneValueError, TypeError):
                        LOG.debug("Values for metrics are not there.")

            if self.options.iterations is not None:
                iterations += 1
                if iterations >= self.options.iterations:
                    break
                elif iterations == 0:
                    iterations = 1

def run_colmet(options):
    LOG.info("Starting Colmet")
    if 'none' in options.input_backends or len(options.input_backends) == 0:
        raise NotEnoughInputBackend()
    else:
        LOG.info("Using %s as input backend" % (options.input_backends))
        input_backend_classes = [ get_input_backend_class(ib_name) for ib_name in options.input_backends ]
        input_backends = [ cls(options) for cls in input_backend_classes ]

    if options.procstats:
        LOG.info("Using procstats as additionnal input backend")
        input_procstat_backends = get_input_backend_class("procstats")
        input_backends.append(input_procstat_backends(options))

    if 'none' in options.output_backends or len (options.output_backends) == 0:
        LOG.warn("Disable any output backend")
        output_backends = [ ]
    else:
        LOG.info("Using %s as the output backend" % (options.output_backends))
        output_backend_classes = [ get_output_backend_class(ob_name) for ob_name in options.output_backends ]
        output_backends = [ cls(options) for cls in output_backend_classes ]

    LOG.debug("Initialize the main loop")

    # Currently support one input/output backend at time.
    if len(input_backends) > 2 or len(output_backends) > 1:
        raise MultipleBackendsNotYetSupported()

    batch = TaskMonBatch(input_backends, output_backends, options)

    LOG.debug("Run the main loop")
    batch.run()
    LOG.info("Ending Colmet")

#
# Main program
#

USAGE = '''%s [OPTIONS]

Display and/or collect cpu, memory and i/o bandwidth used by the processes in a
cpuset or a cgroup.''' % sys.argv[0]

def main():
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        print 'unable to set locale, falling back to the default locale'

    parser = optparse.OptionParser(usage=USAGE, version='colmet ' + VERSION)

    parser.add_option('-n', '--iter', type='int', dest='iterations',
                      metavar='NUM',
                      help='number of iterations before ending [infinite]')
    parser.add_option('-d', '--delay', type='float', dest='delay_seconds',
                      help='delay between iterations [1 second]',
                      metavar='SEC', default=1)

    parser.add_option('-s', '--sample-period', type='float', dest='sampling_period',
                      help='sampling period of measuring [5 second]',
                      metavar='SEC', default=5)

    parser.add_option('--daemon', dest='run_as_daemon',
                      help='Run as daemon [False]',
                      action='store_true',default=False)
    parser.add_option('--pidfile', dest='pidfile',type="str",
                      help='pid file when running as daemon [/var/run/colmet.pid]',
                      default="/var/run/colmet.pid")

    parser.add_option('--logfile', dest='logfile',type="str",
                      help='pid file when running as daemon [/var/log/colmet.log]',
                      default="/var/log/colmet.log")

    parser.add_option('-j', '--job', type='int', dest='job_id',
                      default = [], action='append',
                      help='Job id concerned by the input backend. Depending on the input backend, you can specify several job', metavar='JOB')

    parser.add_option('--jmin', type='int', dest='job_min_id',
                      default = None,
                      help='Job id concerned by the input backend. Depending on the input backend, you can specify an interval of job. This is the minimum', metavar='JOB')

    parser.add_option('--jmax', type='int', dest='job_max_id',
                      default = None,
                      help='Job id concerned by the input backend. Depending on the input backend, you can specify an interval of job. This is the minimum', metavar='JOB')

    parser.add_option('-w', '--walltime', type='int', dest='walltime',
                      default = None,
                      help='Specify the maximum walltime for colmet. If specified, colmet will exit after the specified time (in seconds)')

    parser.add_option('--procstats', action="store_true", dest="procstats",
                      default = False,
                      help='Node monitoring based on some /proc subdirectories contents. Measures are associated to the fictive job with 0 as identifier (job_id)')


    oblist = ", ".join(get_output_backend_list())
    iblist = ", ".join(get_input_backend_list())
    parser.add_option('-o','--output',type='str', dest='output_backends',
                      action = 'append', default = [],
                      help='Specify the output backend. The current supported backends are: %s. By default it is [none]' % (oblist) , metavar='OUTPUT')
    parser.add_option('-i','--input', type='str', dest='input_backends',
                      action = 'append', default = [],
                      help='Specify the input backend. The current supported backends are: %s. By default it is [none]' % (iblist), metavar='INPUT')
    parser.add_option('-v','--verbose',action='count', dest="verbosity",
                      default=0)


    group = optparse.OptionGroup(parser, "[backend] taskstat")

    group.add_option('-c', '--cgroup', type='str', dest='cgroups',
                      action='append', default = [],
                      help='cgroup/cpuset to monitor', metavar='CGROUP')
    group.add_option('-p', '--pid', type='int', dest='pids',
                      action='append', default = [],
                      help='process id to monitor', metavar='PID')
    group.add_option('-t', '--tid', type='int', dest='tids',
                      action='append', default = [],
                      help='task ids to monitor', metavar='TID')
    group.add_option('--cpuset_rootpath', type='str', dest='cpuset_rootpath',
                      action='append', default = [],
                      help='cpuset root path', metavar='CPUSETROOTPATH')
    group.add_option('--regex_job_id', type='str', dest='regex_job_id',
                      action='append', default = ['_(\d+)$'],
                      help='regular expression to extract job_id from cpuset directory name', metavar='REGEXJOBID')

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "[backend] zeromq")
    group.add_option( "--zeromq-uri", type = 'str',
                     dest ='zeromq_uri', default= 'tcp://127.0.0.1:5556')
    group.add_option( "--zeromq-bind-uri", type = 'str',
                     dest ='zeromq_bind_uri', default= 'tcp://0.0.0.0:5556')

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "[backend] hdf5 (output)")
    group.add_option( "--hdf5-output-filepath", type = 'str',
                     help='The file path used to store the hdf5 data',
                     dest ='hdf5_output_filepath', default= '/tmp/colmet/hdf5/counters.hdf5')

    group.add_option( "--hdf5-output-onefileperjob", dest ='hdf5_output_onefileperjob',
                     help='Tell colmet to create one file per job to store the metrics [False]',
                     action='store_true', default= False)

    group.add_option( "--hdf5-output-basedir", type = 'str',
                     help='The base directory used to store hdf5 datai (used when creating a file per job)',
                     dest ='hdf5_output_basedir', default= '/tmp/colmet/hdf5')

    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "[backend] hdf5 (input)")

    group.add_option( "--hdf5-input-filepath", type = 'str',
                     help='The file path used to store the hdf5 data',
                     dest ='hdf5_input_filepath', default= '/tmp/colmet/hdf5/counters.hdf5')

    group.add_option( "--hdf5-input-onefileperjob", dest ='hdf5_input_onefileperjob',
                     help='Tell colmet to create one file per job to store the metrics [False]',
                     action='store_true', default= False)

    group.add_option( "--hdf5-input-basedir", type = 'str',
                     help='The base directory used to store hdf5 datai (used when creating a file per job)',
                     dest ='hdf5_input_basedir', default= '/tmp/colmet/hdf5')


    parser.add_option_group(group)


    options, args = parser.parse_args()
    if args:
        parser.error('Unexpected arguments: ' + ' '.join(args))

    # Set the logging value (always display CRITICAL and ERROR)
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt = '%d/%m/%Y %H:%M:%S',
        level=40-options.verbosity *10,
    )


    # run
    main_loop = lambda: run_colmet(options)
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

    sys.exit(0)


if __name__ == '__main__':
    main()
