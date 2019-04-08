import os
import re
import errno
import struct
import copy
import logging
import ctypes

from colmet.common.metrics.PAPIstats import PAPIstatsCounters
from colmet.common.exceptions import (NoEnoughPrivilegeError,
                                      JobNeedToBeDefinedError)
from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job

LOG = logging.getLogger()


class PAPIstatsBackend(InputBaseBackend):
    __backend_name__ = "PAPIstats"

    def open(self):
        self.jobs = {}

        self.papistats = PAPIStats(self.options)
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

    def get_papi_stats(self, job_id):
        return self.papistats.get_stats(self.filenames[str(job_id)])

    def pull(self):
        for job in self.jobs.values():
            job.update_stats()
        return [job.get_stats() for job in self.jobs.values()]

    def get_counters_class(self):
        return PAPIstatsCounters

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
            options.PAPI = True
            self.jobs[job_id] = Job(self, int(job_id), options)
        # Del ended jobs

        for job_id in (monitored_job_ids - job_ids):
            del self.jobs[job_id]
        # udpate job_id list to monitor
        self.job_id_list = list(job_ids)

class PAPIStats(object):

    def __init__(self, option):
        self.options = option
        self.isInit = False

    def get_stats(self, job_filename):
        if not self.isInit:
            self.PAPIlib = ctypes.cdll.LoadLibrary("./lib_papi.so")    

            job_id_str = ctypes.create_string_buffer(str("/oar/") + job_filename)
            job_id_p = (ctypes.c_char_p)(ctypes.addressof(job_id_str))
            self.PAPIlib.init_counters(job_id_p)

            self.PAPIlib.start_counters()

            self.PAPIvalues = (ctypes.c_uint64 * 3)()
            self.isInit = True

        self.PAPIlib.get_counters(self.PAPIvalues)

        PAPIstats_data = {}
        PAPIstats_data["instructions"] = self.PAPIvalues[0]
        PAPIstats_data["cachemisses"] = self.PAPIvalues[1]
        PAPIstats_data["pagefaults"] = self.PAPIvalues[2]
                        
        return PAPIstatsCounters(PAPIstats_buffer=PAPIstats_data)