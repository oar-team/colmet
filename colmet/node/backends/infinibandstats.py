import os
import re

from subprocess import check_output

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

    def get_stats(self):
        
        infinibandstats_data = {}
        
        # perfquery = check_output(["/usr/sbin/perfquery", "-x"])
        perfquery = check_output(["/usr/sbin/perfquery"])
        
        m = re.search(r'PortXmitData:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portXmitData'] = 4 * int(m.group(1))
        m = re.search(r'PortRcvData:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portRcvData'] = 4 * int(m.group(1))
        m = re.search(r'PortXmitPkts:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portXmitPkts'] = int(m.group(1))
        m = re.search(r'PortRcvPkts:\.*(\d+)', perfquery)
        if m:
            infinibandstats_data['portRcvPkts'] = int(m.group(1))
                        
        return InfinibandstatsCounters(infinibandstats_buffer=infinibandstats_data)
