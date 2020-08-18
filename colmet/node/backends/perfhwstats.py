import os
import re
import errno
import struct
import time
import copy
import logging
import ctypes

from colmet.common.metrics.perfhwstats import PerfhwstatsCounters
from colmet.common.exceptions import (NoEnoughPrivilegeError,
                                      JobNeedToBeDefinedError)
from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job

LOG = logging.getLogger()

perfhwlib = None


class PerfhwstatsBackend(InputBaseBackend):
    __backend_name__ = "perfhwstats"

    def open(self):
        self.jobs = {}
        self.filenames = {}
        lib_path = os.getenv('LIB_PERFHW_PATH', "/usr/lib/lib_perf_hw.so")
        global perfhwlib
        perfhwlib = ctypes.cdll.LoadLibrary(lib_path)

        self.perfhwstats = PerfhwStats(self.options)
        if len(self.job_id_list) < 1 \
                and self.options.cpuset_rootpath == []:
            raise JobNeedToBeDefinedError()
        if len(self.job_id_list) == 1:
            job_id = self.job_id_list[0]
            self.jobs[job_id] = Job(self, job_id, self.options)
        else:
            for i, job_id in enumerate(self.job_id_list):
                self.jobs[job_id] = Job(self, job_id, self.options)

    def close(self):
        pass

    def get_perfhw_stats(self, job_id):
        if str(job_id) in self.filenames:
            return self.perfhwstats.get_stats(self.filenames[str(job_id)])
        else:
            LOG.warning("Perfwhstats: no job with id " + str(job_id) + " to monitor!")

    def pull(self):
        values=list(self.jobs.values())
        for job in values:
            job.update_stats()
        return [job.get_stats() for job in values]

    def get_counters_class(self):
        return PerfhwstatsCounters

    def create_options_job_cgroups(self, cgroups):
        # options are duplicated to allow modification per jobs, here
        # cgroups parametter
        options = copy.copy(self.options)
        options.cgroups = cgroups
        return options

    def update_job_list(self):
        """Used to maintained job list upto date by adding new jobs and
        removing ones to monitor accordingly to cpuset_rootpath and
        regex_job_id.
        """
        cpuset_rootpath = self.options.cpuset_rootpath[0]
        regex_job_id = self.options.regex_job_id[0]

        job_ids = set([])
        # self.filenames = {}
        for filename in os.listdir(cpuset_rootpath):
            jid = re.findall(regex_job_id, filename)
            if len(jid) > 0:
                job_ids.add(jid[0])
                self.filenames[jid[0]] = filename

        monitored_job_ids = set(self.job_id_list)
        # Add new jobs
        for job_id in (job_ids - monitored_job_ids):
            job_path = cpuset_rootpath + "/" + self.filenames[job_id]
            options = self.create_options_job_cgroups([job_path])
            self.jobs[job_id] = Job(self, int(job_id), options)
        # Del ended jobs

        for job_id in (monitored_job_ids - job_ids):
            global perfhwlib
            job_name = self.filenames[job_id]
            job_name_buffer = ctypes.create_string_buffer(b"/oar/" + bytes(job_name, 'utf-8'))
            job_id_p = ctypes.c_char_p(ctypes.addressof(job_name_buffer))
            perfhwlib.remove_cgroup(job_id_p)
            del self.filenames[job_id]
            del self.jobs[job_id]
        # udpate job_id list to monitor
        self.job_id_list = list(job_ids)


class PerfhwStats(object):

    def __init__(self, option):
        self.options = option
        self.isInit = False
        self.perfhwvalues = None

        self.max_nb_counter = 5

        if len(self.options.perfhw_list) > self.max_nb_counter:
            LOG.warning("too many perf counters, kept the first " + str(self.max_nb_counter) + "counters")
            self.options.perfhw_list = self.options.perfhw_list[:self.max_nb_counter]

        self.nb_counters = len(self.options.perfhw_list)

        metrics_mapping = open("./perfhw_mapping." + str(time.time()) + ".csv", "w+")

        for i in range(self.max_nb_counter):
            metric_name = self.options.perfhw_list[i] if i < self.nb_counters else "no_counter"
            metrics_mapping.write("counter" + str(i+1) + "," + metric_name + "\n")

    def get_stats(self, job_filename):
        global perfhwlib
        job_id_str = ctypes.create_string_buffer(b"/oar/" + bytes(job_filename, 'utf-8'))
        job_id_p = (ctypes.c_char_p)(ctypes.addressof(job_id_str))

        perf_counters = ','.join(self.options.perfhw_list)

        perf_counters_b = ctypes.create_string_buffer(perf_counters.encode("utf-8"))
        perf_counters_p = (ctypes.c_char_p)(ctypes.addressof(perf_counters_b))

        perfhwlib.init_cgroup(job_id_p, perf_counters_p)
        self.perfhwvalues = (ctypes.c_uint64 * self.nb_counters)()

        if perfhwlib.get_counters(self.perfhwvalues, job_id_p) == 0:  # c lib returning values successfully
            perfhwstats_data = {
                "counter_1": self.perfhwvalues[0] if self.nb_counters>=1 else -1,
                "counter_2": self.perfhwvalues[1] if self.nb_counters>=2 else -1,
                "counter_3": self.perfhwvalues[2] if self.nb_counters>=3 else -1,
                "counter_4": self.perfhwvalues[3] if self.nb_counters>=4 else -1,
                "counter_5": self.perfhwvalues[4] if self.nb_counters>=5 else -1,
            }
        else:
            perfhwstats_data = {
                "counter_1": -1,
                "counter_2": -1,
                "counter_3": -1,
                "counter_4": -1,
                "counter_5": -1,
            }
            LOG.warning("cannot get perf_event counters values, replaced by -1 values")

        return PerfhwstatsCounters(perfhwstats_buffer=perfhwstats_data)
