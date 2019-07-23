
import struct
import logging


LOG = logging.getLogger()

from .base import UInt8, UInt16, UInt32, UInt64, Int64, String, BaseCounters


class PerfhwstatsCounters(BaseCounters):
    __metric_name__ = 'perfhwstats_default'

    counters_perfhwstats = {
        'counter1': (Int64(), 'count', 'none', 'counter1'),
        'counter2': (Int64(), 'count', 'none', 'counter2'),
        'counter3': (Int64(), 'count', 'none', 'counter3'),
        'counter4': (Int64(), 'count', 'none', 'counter4'),
        'counter5': (Int64(), 'count', 'none', 'counter5'),
    }

    counters_perfhwstats_to_get = [
        "counter1",
        "counter2",
        "counter3",
        "counter4",
        "counter5",

    ]

    _counters = []
    for c_name in counters_perfhwstats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_perfhwstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(taskstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, taskstat_backend, job_id):
        return taskstat_backend.get_perfhw_stats(job_id)

    def __init__(self, perfhwstats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif perfhwstats_buffer is None:
            self._empty_fill()
        else:
            for name in PerfhwstatsCounters._counter_definitions:
                self._counter_values[name] = perfhwstats_buffer[name]
