import os
import re
import copy
import errno
import struct
import time
import logging

from subprocess import check_output, STDOUT, CalledProcessError

from colmet.common.metrics.nvidiastats import NvidiastatsCounters
from colmet.common.exceptions import (NoEnoughPrivilegeError,
                                      JobNeedToBeDefinedError)
from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job

LOG = logging.getLogger()


class NvidiastatsBackend(InputBaseBackend):
    __backend_name__ = "nvidiastats"

    def open(self):
        self.jobs = {}
        self.filenames = {}

        self.nvidiastats = nvidiaStats(self.options)
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

    def get_nvidia_stats(self, job_id):
        if str(job_id) in self.filenames:
            return self.nvidiastats.get_stats(self.filenames[str(job_id)])

    def pull(self):
        values=list(self.jobs.values())
        for job in values:
            job.update_stats()
        return [job.get_stats() for job in values]

    def get_counters_class(self):
        return NvidiastatsCounters

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
        #self.filenames = {}
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


class nvidiaStats(object):

    def __init__(self, option):
        self.options = option
        self.isInit = False
        self.nvidiavalues = None
        
    def get_stats(self, job_filename):

          nvidiastats_data={}
          counter_names=["uuid","power","temperature","utilization-gpu","utilization-memory","memory-total","memory-free","memory-used"] 
          for name in counter_names:                                                                               
              if name not in nvidiastats_data.keys() and name != "uuid":
                  nvidiastats_data[name]=0

          # Get the list of pids
          cpuset_rootpath = self.options.cpuset_rootpath[0]
          f=cpuset_rootpath + "/" + job_filename + "/tasks"
          try:
              pids=list(open(f))
          except:
              LOG.warning("nvidiastats: error reading file %s (disapeared?)", f)
              pids=[]
          
          # Get the nvidia running processes
          try:
              processes = check_output(["/usr/bin/nvidia-smi", "--query-compute-apps=pid,gpu_uuid","--format=csv"])
              processes = processes.decode("utf-8")
          except CalledProcessError as e:
              print("Error calling nvidia-smi --query-compute-apps: ", e.returncode)
          gpu_pids={}
          for line in processes.splitlines():
              (p,i)=line.split(', ')
              gpu_pids[p]=i

          # Get the list of GPU devices used by the pids
          gpus=set()
          for pid in pids:
              pid=pid.strip('\n')
              if pid in gpu_pids.keys():
                  gpus.add(gpu_pids[pid])

          # Get the nvidia metrics
          try:
              nvmetrics = check_output(["/usr/bin/nvidia-smi", "--query-gpu=uuid,power.draw,temperature.gpu,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used", "--format=csv"])
              nvmetrics = nvmetrics.decode("utf-8")
          except CalledProcessError as e:
              print("Error calling nvidia-smi --query-gpu: ", e.returncode)
          gpu_metrics={}
          for line in nvmetrics.splitlines():
              line=re.sub(' W| %| GiB| MiB| KiB','',line)
              values=line.split(', ')
              data=dict(zip(counter_names,values))
              if data["uuid"] in gpus:
                  for name in counter_names:
                      if name == "temperature":
                          nvidiastats_data[name]=int(float(data[name]))
                      elif name != "uuid":
                          nvidiastats_data[name]+=int(float(data[name]))

          return NvidiastatsCounters(nvidiastats_buffer=nvidiastats_data)
