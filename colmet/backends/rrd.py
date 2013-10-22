'''
stdout backend : print information to stdout
'''

import os
import logging
import pyrrd.rrd as rrd

LOG = logging.getLogger()

from colmet.metrics.base import get_counters_class, get_rrd_class
from colmet.backends.base import OutputBaseBackend, InputBaseBackend

def get_output_backend_class():
    return RRDOutputBackend


class RRDOutputBackend(OutputBaseBackend):
    '''
    stdout backend class
    '''
    @classmethod
    def _get_backend_name(cls):
        return "rrd"

    def __init__(self, options):
        OutputBaseBackend.__init__(self,options)
        self.stat_buffer = dict()

        self.jobs = {}

    def _get_job_stat(self,job_id):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobFile(self.options,job_id)
        return self.jobs[job_id]

    def push(self, counters_list):
        '''
        put the metrics to the output backend
        '''
        counters_dict = dict()
        for counters in counters_list:
            job_id = counters._get_header('job_id')
            if job_id not in counters_dict:
                counters_dict[job_id] = list()
            counters_dict[job_id].append(counters)

        for (job_id,c_list) in counters_dict.iteritems():
            jobstat = self._get_job_stat(job_id)
            jobstat.append_stats(c_list)

class FileAccess(object):
    '''
    Share the access to one or several between each monitored job
    '''
    def __init__(self):
        self.files = dict()

    def getRRD(self,path,datasources,roundrobinarchives,timestamp_start,step):
        if path in self.files:
            rrd_file = self.files[path]
        else:
            rrd_file = rrd.RRD(
                path,
                ds=datasources,
                rra=roundrobinarchives,
                start=timestamp_start,
                step=step
            )
            if os.path.isfile(path):
                os.unlink(path)
            rrd_file.create()
            self.files[path] = rrd_file
        return rrd_file

class JobFile(object):
    fileaccess = FileAccess()

    path_level = 7

    MAX_VALUES_PER_UPDATE = 100

    def __init__(self,options,job_id):
        self.options = options
        self.job_id = job_id
        self.rrd_class = None
        self.metric_class = None
        self.metric_backend = None

        if hasattr(options,'rrd_basedir'):
            self.rrd_basedir = options.rrd_basedir
        else:
            self.rrd_basedir = "/tmp/colmet/rrd"

        if hasattr(options,'rrd_step'):
            self.rrd_step = options.rrd_step
        else:
            self.rrd_step = 1

        if hasattr(options,'rrd_destdir'):
            self.rrd_destdir = options.rrd_destdir
        else:
            self.rrd_destdir = None

        if hasattr(options,'ts_start'):
            self.ts_start = options.ts_start
        else:
            self.ts_start = None

        if hasattr(options,'ts_stop'):
            self.ts_stop = options.ts_stop
        else:
            self.ts_stop = None

        self.job_dir = self._get_job_dir()
        if not os.path.exists(self.job_dir):
            os.makedirs(self.job_dir)

        LOG.debug("Writing counters in rrd format for job %s" % self.job_id)

    def _get_job_dir(self):
        if self.rrd_destdir == None:
            i = 0
            job_id_s = str(self.job_id).zfill(self.path_level)
            path = ""
            while(i < self.path_level):
                path = os.path.join(
                    path,
                    job_id_s[i]
                )
                i+=1

            path = os.path.join(self.rrd_basedir,path)
            path = os.path.join(path,"job_%s" % self.job_id)
        else:
            path = self.rrd_destdir
        return path

    def _get_job_rrd_path(self, hostname):
        return os.path.join(self.job_dir, "%s.rrd" %hostname)

    def _get_rrd_file(self,path):
        return self.fileaccess.getRRD(
            path,
            self.rrd_class.datasources.values(),
            self.rrd_class.get_rra(self.ts_start,self.ts_stop),
            self.ts_start,
            self.rrd_step
        )

    def append_stats(self,stats):

        self.metric_name = stats[0].header_values['metric_backend']
        self.metric_class = get_counters_class(self.metric_name)
        self.rrd_class = get_rrd_class(self.metric_name)

        sorted_stats = sorted(stats, key=lambda item: item.header_values['timestamp'])

        if self.ts_start == None:
            self.ts_start = sorted_stats[0].header_values['timestamp'] - 1
        if self.ts_stop == None:
            self.ts_stop = sorted_stats[-1].header_values['timestamp'] + 1

        rrd_stats = [ metric for metric in sorted_stats if self.ts_start < metric.header_values['timestamp'] < self.ts_stop ]


        rrd_dict = dict()
        for stat in rrd_stats:
            rrd_path = self._get_job_rrd_path(stat.header_values['hostname'])
            rrd_file = self._get_rrd_file(rrd_path)
            if rrd_path in rrd_dict:
                if rrd_dict[rrd_path] > self.MAX_VALUES_PER_UPDATE:
                    rrd_file.update()
                    rrd_dict[rrd_path] = 0
                else:
                    rrd_dict[rrd_path] += 1

            else:
                rrd_dict[rrd_path] = 1

            self.rrd_class.to_rrd(rrd_file, stat)

        for (rrd_path, nb_in_buffer) in rrd_dict.iteritems():
            rrd_file = self._get_rrd_file(rrd_path)
            if (nb_in_buffer > 0):
                rrd_file.update()
            self.rrd_class.to_graph(rrd_file, self.ts_start,self.ts_stop,self.rrd_step)


