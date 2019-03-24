import os
import re

from subprocess import check_output

from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.RAPLstats import InfinibandstatsCounters



class RAPLBackend(InputBaseBackend):
    __backend_name__ = "RAPLstats"

    def open(self):
        self.RAPLstats = RAPLStats(self.options)
        # job with id equal to 0 is the fictive job to gather nodes' monitoring
        # measures
        self.job_0 = Job(self, 0, self.options)

    def close(self):
        pass

    def get_RAPLstats(self):
        counters = self.RAPLstats.get_stats()
        return counters

    def get_counters_class(self):
        return RAPLstatsCounters

    def pull(self):
        self.job_0.update_stats()
        return self.job_0.get_stats()


class RAPLstats(object):

    def __init__(self, option):
        self.options = option

    def get_stats(self):
        RAPLstats_data = {}

        RAPLstats_data["maxEnergyRangeUJ"] = 1234
        RAPLstats_data["energyUJ"] = 1234

        return RAPLstatsCounters(RAPLstats_buffer=RAPLstats_data)
