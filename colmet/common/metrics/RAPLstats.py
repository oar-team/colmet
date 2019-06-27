import logging
import ctypes
import os

LOG = logging.getLogger()

from .base import String, UInt64, Int64, BaseCounters


class RAPLstatsCounters(BaseCounters):

    __metric_name__ = 'RAPLstats_default'

    lib_path = os.getenv('LIB_RAPL_PATH', "/usr/lib/lib_rapl.so")
    raplLib = ctypes.cdll.LoadLibrary(lib_path)

    raplLib.init_rapl()

    # raplsize = raplLib.get_rapl_size()
    raplsize = 12 # we assume there are 4 cpu per node, il less we will return -1 metrics



    #def __init__(self):
    counters_RAPLstats = {}
    nbr_zones = 4
    for i in range(raplsize):
        counters_RAPLstats["name_" + str(i)] = (String(255), 'string', 'none', '')
        counters_RAPLstats["maxEnergyRangeUJ_" + str(i)] = (Int64(), 'count', 'none', 'maxEnergyRangeUJ')
        counters_RAPLstats["energyUJ_" + str(i)] = (Int64(), 'count', 'none', 'energyUJ')

    counters_RAPLstats_to_get = []

    for i in range(raplsize):
        counters_RAPLstats_to_get.append("name_" + str(i))
        counters_RAPLstats_to_get.append("maxEnergyRangeUJ_" + str(i))
        counters_RAPLstats_to_get.append("energyUJ_" + str(i))

    _counters = []

    for c_name in counters_RAPLstats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_RAPLstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))
    @classmethod
    def get_zero_counters(cls):
        return cls(RAPLstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, RAPLstats_backend):
        return RAPLstats_backend.get_RAPLstats()

    def __init__(self, RAPLstats_buffer=None, raw=None):

        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif RAPLstats_buffer is None:
            self._empty_fill()
        else:
            for name in RAPLstatsCounters._counter_definitions:
                self._counter_values[name] = RAPLstats_buffer[name]
