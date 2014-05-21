'''
stdout backend : print information to stdout
'''

import os
import logging

from pyrrd.graph import DEF, LINE, Graph
from pyrrd.rrd import DataSource, RRA, RRD

LOG = logging.getLogger()

from colmet.common.metrics import get_counters_class
from colmet.common.backends.base import OutputBaseBackend


class RRDCounters(object):

    def __init__(self, metric_name):
        self.counters_class = get_counters_class(metric_name)
        self.datasources = dict()
        for c_key in self.counters_class._counter_definitions.keys():
            rrd_key = c_key[0:19]
            self.datasources[rrd_key] = DataSource(dsName=rrd_key,
                                                   dsType='GAUGE',
                                                   heartbeat=600,)

    def get_rra(self, ts_start, ts_end, step=1):
        nb_rows = (ts_end - ts_start) / step
        return [
            RRA(cf='AVERAGE', xff=0.5, steps=step, rows=nb_rows),
            RRA(cf='LAST', xff=0.5, steps=step, rows=nb_rows),
            RRA(cf='MIN', xff=0.5, steps=step, rows=nb_rows),
            RRA(cf='MAX', xff=0.5, steps=step, rows=nb_rows),
            RRA(cf='AVERAGE', xff=0.5, steps=5, rows=nb_rows),
            RRA(cf='AVERAGE', xff=0.5, steps=5, rows=nb_rows / 5),
            RRA(cf='AVERAGE', xff=0.5, steps=15, rows=nb_rows / 15),
        ]

    @classmethod
    def to_rrd(cls, myRRD, counters):
        c_list = [counters._get_counter(c_key) for c_key in counters._counter_definitions.keys()]

        myRRD.bufferValue(str(counters.timestamp), *c_list)

    def to_graph(self, rrd_file, ts_start, ts_end, width, height, step=1):

        graphfile_base = os.path.splitext(rrd_file.filename)[0]
        defs = dict()
        for c_key in self.counters_class._counter_definitions.keys():
            rrd_key = c_key[0:19]

            gdef = DEF(
                rrdfile=rrd_file.filename,
                vname=rrd_key,
                dsName=self.datasources[rrd_key].name,
                step=step,
                start=str(ts_start),
                end=str(ts_end)
            )

            gline = LINE(defObj=gdef, color='#000099', legend="%s (%s)" % (self.counters_class._counter_definitions[c_key][3], rrd_key))
            defs[rrd_key] = [gdef, gline]

        for c_key in self.counters_class._counter_definitions.keys():
            rrd_key = c_key[0:19]
            graphfile_name = "%s_%s.png" % (graphfile_base, rrd_key)
            g = Graph(
                graphfile_name,
                start=ts_start, end=ts_end,
                vertical_label=self.counters_class._counter_definitions[c_key][1],
                imgformat='png',
                width=600,
                height=300
            )
            g.data.extend(defs[rrd_key])
            g.write()


class RRDOutputBackend(OutputBaseBackend):
    '''
    stdout backend class
    '''
    __backend_name__ = "rrd"

    def open(self):
        self.stat_buffer = dict()
        self.jobs = {}

    def close(self):
        pass

    def _get_job_stat(self, job_id):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobFile(self.options, job_id)
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

        for (job_id, c_list) in counters_dict.iteritems():
            jobstat = self._get_job_stat(job_id)
            jobstat.append_stats(c_list)


class FileAccess(object):
    '''
    Share the access to one or several between each monitored job
    '''
    def __init__(self):
        self.files = dict()

    def getRRD(self, path, datasources, roundrobinarchives, timestamp_start,
               step):
        if path in self.files:
            rrd_file = self.files[path]
        else:
            rrd_file = RRD(
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

    MAX_VALUES_PER_UPDATE = 100

    def __init__(self, options, job_id):
        self.options = options
        self.job_id = job_id
        self.rrd_counters = None
        self.metric_class = None
        self.metric_backend = None

        if hasattr(options, 'rrd_basedir'):
            self.rrd_basedir = options.rrd_basedir
        else:
            self.rrd_basedir = "/tmp/colmet/rrd"

        if hasattr(options, 'rrd_step'):
            self.rrd_step = options.rrd_step
        else:
            self.rrd_step = 1

        if hasattr(options, 'rrd_ts_start'):
            self.ts_start = options.ts_start
        else:
            self.ts_start = None

        self.rrd_graph_width = options.rrd_graph_width
        self.rrd_graph_height = options.rrd_graph_height

        if hasattr(options, 'rrd_ts_stop'):
            self.ts_stop = options.ts_stop
        else:
            self.ts_stop = None

        if hasattr(options, 'rrd_path_level'):
            self.path_level = options.rrd_path_level

        self.job_dir = self._get_job_dir()
        if not os.path.exists(self.job_dir):
            os.makedirs(self.job_dir)

        LOG.debug("Writing counters in rrd format for job %s" % self.job_id)

    def _get_job_dir(self):
        i = 0
        job_id_s = str(self.job_id).zfill(self.path_level)
        path = ""
        while(i < self.path_level):
            path = os.path.join(
                path,
                job_id_s[i]
            )
            i += 1

        path = os.path.join(self.rrd_basedir, path)
        path = os.path.join(path, "job_%s" % self.job_id)
        return path

    def _get_job_rrd_path(self, hostname):
        return os.path.join(self.job_dir, "%s.rrd" % hostname)

    def _get_rrd_file(self, path):
        return self.fileaccess.getRRD(
            path,
            self.rrd_counters.datasources.values(),
            self.rrd_counters.get_rra(self.ts_start, self.ts_stop),
            self.ts_start,
            self.rrd_step
        )

    def append_stats(self, stats):
        self.metric_name = stats[0].metric_backend
        self.metric_class = get_counters_class(self.metric_name)
        self.rrd_counters = RRDCounters(self.metric_name)

        sorted_stats = sorted(stats, key=lambda item:
                              item.timestamp)

        if self.ts_start is None:
            self.ts_start = sorted_stats[0].timestamp - 1
        if self.ts_stop is None:
            self.ts_stop = sorted_stats[-1].timestamp + 1

        rrd_stats = [metric for metric in sorted_stats
                     if (self.ts_start < metric.timestamp
                         < self.ts_stop)]

        rrd_dict = dict()
        for stat in rrd_stats:
            rrd_path = self._get_job_rrd_path(stat.hostname)
            rrd_file = self._get_rrd_file(rrd_path)
            if rrd_path in rrd_dict:
                if rrd_dict[rrd_path] > self.MAX_VALUES_PER_UPDATE:
                    rrd_file.update()
                    rrd_dict[rrd_path] = 0
                else:
                    rrd_dict[rrd_path] += 1

            else:
                rrd_dict[rrd_path] = 1

            self.rrd_counters.to_rrd(rrd_file, stat)

        for (rrd_path, nb_in_buffer) in rrd_dict.iteritems():
            rrd_file = self._get_rrd_file(rrd_path)
            if (nb_in_buffer > 0):
                rrd_file.update()
            self.rrd_counters.to_graph(rrd_file, self.ts_start, self.ts_stop,
                                       self.rrd_step, self.rrd_graph_width,
                                       self.rrd_graph_height)
