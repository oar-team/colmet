
import struct
import logging


LOG = logging.getLogger()

from .base import UInt8, UInt16, UInt32, UInt64, Int64, String, BaseCounters


class JobprocstatsCounters(BaseCounters):
    __metric_name__ = 'jobprocstats_default'

    counter_names=["rchar","wchar","syscr","syscw","read_bytes","write_bytes","cancelled_write_bytes"]

    counters_jobprocstats = {}
    counters_jobprocstats_to_get = []

    for name in counter_names:
        counters_jobprocstats[name]=(Int64(), 'count', 'none', name)
        counters_jobprocstats_to_get.append(name)

    _counters = []
    for c_name in counters_jobprocstats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_jobprocstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(jobprocstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, jobprocstats_backend, job_id):
        return jobprocstats_backend.get_jobproc_stats(job_id)

    def __init__(self, jobprocstats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif jobprocstats_buffer is None:
            self._empty_fill()
        else:
            for name in JobprocstatsCounters._counter_definitions:
                self._counter_values[name] = jobprocstats_buffer[name]
