import os
import re
import glob
import json

from subprocess import check_output, STDOUT, CalledProcessError

from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.infinibandstats import InfinibandstatsCounters



class InfinibandstatsBackend(InputBaseBackend):
    __backend_name__ = "infinibandstats"

    def open(self):
        self.infinibandstats = InfinibandStats(self.options)
        # job with id equal to 0 is the fictive job to gather nodes' monitoring
        # measures
        self.job_0 = Job(self, 0, self.options)

    def close(self):
        pass

    def get_infinibandstats(self):
        counters = self.infinibandstats.get_stats()
        return counters

    def get_counters_class(self):
        return InfinibandstatsCounters

    def pull(self):
        self.job_0.update_stats()
        return self.job_0.get_stats()


class InfinibandStats(object):

    def __init__(self, option):
        self.options = option

    def get_running_jobs(self):
        job_ids=[]
        if os.path.exists("/dev/cpuset/oar"):
            cwd = os.getcwd()
            os.chdir("/dev/cpuset/oar")
            for file in glob.glob("*_*"):
                m = re.search('.*_(\d+)',file)
                if m is not None:
                    job_ids.append(int(m.group(1)))
            os.chdir(cwd)
        return job_ids

    def get_stats(self):

        if self.options.omnipath:
            mult_const = 8
        else:
            mult_const = 4
        
        infinibandstats_data = {}

        perfquery = ""

        try:
            perfquery = check_output(["/usr/sbin/perfquery", "-x"])
            perfquery = perfquery.decode("utf-8")
        except CalledProcessError as e:
            print("Error calling perfquery : ", e.returncode)

        m = re.search(r'PortXmitData:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portXmitData'] = mult_const * int(m.group(1))
        else:
            infinibandstats_data['portXmitData'] = -1

        m = re.search(r'PortRcvData:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portRcvData'] = mult_const * int(m.group(1))
        else:
            infinibandstats_data['portRcvData'] = -1

        m = re.search(r'PortXmitPkts:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portXmitPkts'] = int(m.group(1))
        else:
            infinibandstats_data['portXmitPkts'] = -1

        m = re.search(r'PortRcvPkts:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portRcvPkts'] = int(m.group(1))
        else:
            infinibandstats_data['portRcvPkts'] = -1
    
        jobs=json.dumps(self.get_running_jobs())
        infinibandstats_data['involved_jobs'] = jobs

        return InfinibandstatsCounters(infinibandstats_buffer=infinibandstats_data)
