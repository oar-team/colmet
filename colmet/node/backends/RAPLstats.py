import os
import re
import ctypes

from subprocess import check_output

from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.RAPLstats import RAPLstatsCounters


class RAPLstatsBackend(InputBaseBackend):
    __backend_name__ = "RAPLstats"

    def open(self):
        self.RAPLstats = RAPLstats(self.options)
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
        self.raplLib = ctypes.cdll.LoadLibrary("./lib_rapl.so")
        
        self.raplLib.init_rapl()
        self.raplsize = self.raplLib.get_rapl_size()

        self.maxEnergy = (ctypes.c_uint64 * self.raplsize)()
        self.oldEnergy = (ctypes.c_uint64 * self.raplsize)()

        #First value doesn't mean anything
        self.raplLib.get_powercap_rapl_get_energy_uj(self.oldEnergy)

        #These value won't change
        self.name_buffer = [ctypes.create_string_buffer(255) for i in range(self.raplsize)]
        self.name_pointers = (ctypes.c_char_p*self.raplsize)(*map(ctypes.addressof, self.name_buffer))
        self.raplLib.get_powercap_rapl_name(self.name_pointers)
        self.names = [s.value for s in self.name_buffer]

    def get_stats(self):
        RAPLstats_data = {}

        energy = (ctypes.c_uint64 * self.raplsize)()
        self.raplLib.get_powercap_rapl_get_max_energy_range_uj(self.maxEnergy)
        self.raplLib.get_powercap_rapl_get_energy_uj(energy)
        i = 0
        for i in range(self.raplsize):

            RAPLstats_data["name_" + str(i)] = self.names[i]
            RAPLstats_data["maxEnergyRangeUJ_" + str(i)] = self.maxEnergy[i]
            RAPLstats_data["energyUJ_" + str(i)] = energy[i] - self.oldEnergy[i]

        for i in range(self.raplsize, 12): # assuming 4 cpu x 3 measure per cpu
            RAPLstats_data["name_" + str(i)] = "no value available"
            RAPLstats_data["maxEnergyRangeUJ_" + str(i)] = -1
            RAPLstats_data["energyUJ_" + str(i)] = -1

        self.oldEnergy = energy

        return RAPLstatsCounters(RAPLstats_buffer=RAPLstats_data)
