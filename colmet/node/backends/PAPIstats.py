import os
import re
import errno
import struct
import copy
import logging

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
    """
    def build_request(self, pid):
        return self.taskstats_nl.build_request(pid)

    def get_task_stats(self, request):
        counters = self.taskstats_nl.get_single_task_stats(request)
        return counters
    """
    def get_papi_stats(self, job_id):
        return self.papistats.get_stats(job_id)

    def pull(self):
        for job in self.jobs.values():
            LOG.debug("pull job :" + str(job.job_id))
            job.update_stats()
        return [job.get_stats() for job in self.jobs.values()]

    def get_counters_class(self):
        return PAPIstatsCounters
    """
    def create_options_job_cgroups(self, cgroups):
        # options are duplicated to allow modification per jobs, here
        # cgroups parametter
        options = copy.copy(self.options)
        options.cgroups = cgroups
        return options
    """
    def update_job_list(self):
        """Used to maintained job list upto date by adding new jobs and
        removing ones to monitor accordingly to cpuset_rootpath and
        regex_job_id.
        """
        cpuset_rootpath = self.options.cpuset_rootpath[0]
        regex_job_id = self.options.regex_job_id[0]

        job_ids = set([])
        filenames = {}
        for filename in os.listdir(cpuset_rootpath):
            jid = re.findall(regex_job_id, filename)
            if len(jid) > 0:
                job_ids.add(jid[0])
                filenames[jid[0]] = filename

        monitored_job_ids = set(self.job_id_list)
        # Add new jobs
        for job_id in (job_ids - monitored_job_ids):
            job_path = cpuset_rootpath + "/" + filenames[job_id]
            #options = self.create_options_job_cgroups([job_path])
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

    def get_stats(self, job_id):
        PAPIstats_data = {}
        PAPIstats_data["papi_nb_read"] = int(job_id)
        PAPIstats_data["papi_nb_write"] = 5678
                        
        return PAPIstatsCounters(PAPIstats_buffer=PAPIstats_data)