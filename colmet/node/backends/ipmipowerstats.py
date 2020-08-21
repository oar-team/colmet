import os
import re
import glob
import json

from subprocess import check_output, STDOUT, CalledProcessError

from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.ipmipowerstats import IpmipowerstatsCounters



class IpmipowerstatsBackend(InputBaseBackend):
    __backend_name__ = "ipmipowerstats"

    def open(self):
        self.ipmipowerstats = IpmipowerStats(self.options)
        # job with id equal to 0 is the fictive job to gather nodes' monitoring
        # measures
        self.job_0 = Job(self, 0, self.options)

    def close(self):
        pass

    def get_ipmipowerstats(self):
        counters = self.ipmipowerstats.get_stats()
        return counters

    def get_counters_class(self):
        return IpmipowerstatsCounters

    def pull(self):
        self.job_0.update_stats()
        return self.job_0.get_stats()


class IpmipowerStats(object):

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

        ipmipowerstats_data = {}
        query = ""

        try:
            query = check_output(self.options.ipmipower_cmd)
            query = query.decode("utf-8")
        except CalledProcessError as e:
            print("Error calling ipmipower_cmd : ", e.returncode)

        m = re.search('.*: (\d+) .*', query)
        if m:
            ipmipowerstats_data['average_power_consumption'] = int(m.group(1))
        else:
            ipmipowerstats_data['average_power_consumption'] = -1
    
        jobs=json.dumps(self.get_running_jobs())
        ipmipowerstats_data['involved_jobs'] = jobs

        return IpmipowerstatsCounters(ipmipowerstats_buffer=ipmipowerstats_data)
