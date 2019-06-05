import os
import re
import errno
import struct
import copy
import logging
import ctypes

from colmet.common.metrics.perfhwstats import PerfhwstatsCounters
from colmet.common.exceptions import (NoEnoughPrivilegeError,
                                      JobNeedToBeDefinedError)
from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job

LOG = logging.getLogger()


class PerfhwstatsBackend(InputBaseBackend):
    __backend_name__ = "perfhwstats"

    def open(self):
        self.jobs = {}

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
        return self.perfhwstats.get_stats(self.filenames[str(job_id)])

    def pull(self):
        for job in self.jobs.values():
            job.update_stats()
        return [job.get_stats() for job in self.jobs.values()]

    def get_counters_class(self):
        return PerfhwstatsCounters

    def update_job_list(self):
        """Used to maintained job list upto date by adding new jobs and
        removing ones to monitor accordingly to cpuset_rootpath and
        regex_job_id.
        """
        cpuset_rootpath = self.options.cpuset_rootpath[0]
        regex_job_id = self.options.regex_job_id[0]

        job_ids = set([])
        self.filenames = {}
        for filename in os.listdir(cpuset_rootpath):
            jid = re.findall(regex_job_id, filename)
            if len(jid) > 0:
                job_ids.add(jid[0])
                self.filenames[jid[0]] = filename

        monitored_job_ids = set(self.job_id_list)
        # Add new jobs
        for job_id in (job_ids - monitored_job_ids):
            job_path = cpuset_rootpath + "/" + self.filenames[job_id]
            options =  self.options
            options.perfhw = True
            self.jobs[job_id] = Job(self, int(job_id), options)
        # Del ended jobs

        for job_id in (monitored_job_ids - job_ids):
            del self.jobs[job_id]
        # udpate job_id list to monitor
        self.job_id_list = list(job_ids)

class PerfhwStats(object):

    def __init__(self, option):
        self.options = option
        self.isInit = False

    def get_stats(self, job_filename):
        if not self.isInit:
            self.perfhwlib = ctypes.cdll.LoadLibrary("./lib_perf_hw.so")    

            job_id_str = ctypes.create_string_buffer(b"/oar/" + bytes(job_filename, 'utf-8'))
            job_id_p = (ctypes.c_char_p)(ctypes.addressof(job_id_str))
            self.perfhwlib.init_counters(job_id_p)

            self.perfhwlib.start_counters()

            self.perfhwvalues = (ctypes.c_uint64 * 3)()
            self.isInit = True

        self.perfhwlib.get_counters(self.perfhwvalues)

        perfhwstats_data = {}
        perfhwstats_data["instructions"] = self.perfhwvalues[0]
        perfhwstats_data["cachemisses"] = self.perfhwvalues[1]
        perfhwstats_data["pagefaults"] = self.perfhwvalues[2]
                        
        return PerfhwstatsCounters(perfhwstats_buffer=perfhwstats_data)