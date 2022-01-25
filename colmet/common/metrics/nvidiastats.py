
import struct
import logging


LOG = logging.getLogger()

from .base import UInt8, UInt16, UInt32, UInt64, Int64, String, BaseCounters


class NvidiastatsCounters(BaseCounters):
    __metric_name__ = 'nvidiastats_default'

    counter_names=["power","temperature","utilization-gpu","utilization-memory","memory-total","memory-free","memory-used"]

    counters_nvidiastats = {}
    counters_nvidiastats_to_get = []

    for name in counter_names:
        counters_nvidiastats[name]=(Int64(), 'count', 'none', name)
        counters_nvidiastats_to_get.append(name)

    _counters = []
    for c_name in counters_nvidiastats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_nvidiastats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(nvidiastats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, nvidiastats_backend, job_id):
        return nvidiastats_backend.get_nvidia_stats(job_id)

    def __init__(self, nvidiastats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif nvidiastats_buffer is None:
            self._empty_fill()
        else:
            for name in NvidiastatsCounters._counter_definitions:
                self._counter_values[name] = nvidiastats_buffer[name]
