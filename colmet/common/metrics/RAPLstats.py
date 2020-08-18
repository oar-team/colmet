import logging
import ctypes
import os

LOG = logging.getLogger()

from .base import String, UInt64, Int64, BaseCounters


class RAPLstatsCounters(BaseCounters):

    __metric_name__ = 'RAPLstats_default'

    # raplsize = raplLib.get_rapl_size()
    raplsize = 24 # we assume there are 4 cpu per node * 3 zones per cpu * 2 metrics per cpu, if less we will return -1 metrics

    #def __init__(self):
    counters_RAPLstats = {}
    for i in range(raplsize):
        counters_RAPLstats["counter_" + str(i+1)] = (Int64(), 'count', 'none', "counter" + str(i+1))

    counters_RAPLstats_to_get = []

    for i in range(raplsize):
        counters_RAPLstats_to_get.append("counter_" + str(i+1))

    counters_RAPLstats["involved_jobs"] = (String(8192), 'string', 'none', 'involved_jobs')
    counters_RAPLstats_to_get.append("involved_jobs")

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
