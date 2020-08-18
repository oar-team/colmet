import os
import re
import copy
import errno
import struct
import time
import logging

from colmet.common.metrics.jobprocstats import JobprocstatsCounters
from colmet.common.exceptions import (NoEnoughPrivilegeError,
                                      JobNeedToBeDefinedError)
from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job

LOG = logging.getLogger()


class JobprocstatsBackend(InputBaseBackend):
    __backend_name__ = "jobprocstats"

    def open(self):
        self.jobs = {}
        self.filenames = {}

        self.jobprocstats = jobprocStats(self.options)
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

    def get_jobproc_stats(self, job_id):
        return self.jobprocstats.get_stats(self.filenames[str(job_id)])

    def pull(self):
        values=list(self.jobs.values())
        for job in values:
            job.update_stats()
        return [job.get_stats() for job in values]

    def get_counters_class(self):
        return JobprocstatsCounters

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
            del self.filenames[job_id]
            del self.jobs[job_id]

        # udpate job_id list to monitor
        self.job_id_list = list(job_ids)


class jobprocStats(object):

    def __init__(self, option):
        self.options = option
        self.isInit = False
        self.jobprocvalues = None
        # init counters for iostats
        self.jobprocstats_data={}
        counter_names=["rchar","wchar","syscr","syscw","read_bytes","write_bytes","cancelled_write_bytes"]       
        for name in counter_names:                                                                               
            if name not in self.jobprocstats_data.keys():
                self.jobprocstats_data[name]=0

    def get_stats(self, job_filename):

          # Get the list of pids
          cpuset_rootpath = self.options.cpuset_rootpath[0]
          f=cpuset_rootpath + "/" + job_filename + "/tasks"
          if os.path.isfile(f):
              pids=list(open(f))
 
             # Sum the metrics
              for pid in pids:
                  pid=pid.strip('\n')
                  f="/proc/"+pid+"/io"
                  if os.path.isfile(f):
                      with open(f) as iostats:
                          for line in iostats:
                              (key,val) = line.split(": ")
                              if key in self.jobprocstats_data.keys():
                                  self.jobprocstats_data[key]+=int(val)
                              else:
                                  self.jobprocstats_data[key]=int(val)
                  else:
                      LOG.debug("jobprocstats: file %s does not exists (pid disapeared?)!",f) 
          else:
              LOG.warning("jobprocstats: file %s does not exists!",f)

          return JobprocstatsCounters(jobprocstats_buffer=self.jobprocstats_data)
