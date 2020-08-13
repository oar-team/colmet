import logging

LOG = logging.getLogger()

from .base import UInt64, Int64, BaseCounters, String


class InfinibandstatsCounters(BaseCounters):
    __metric_name__ = 'infinibandstats_default'

    counters_infinibandstats = {
        # 'key': ( offset,length, type, repr, acc )
        'portXmitData': (Int64(), 'bytes', 'none', 'portXmitData'),
        'portRcvData': (Int64(), 'bytes', 'none', 'portRcvData'),
        'portXmitPkts': (Int64(), 'count', 'none', 'portXmitPkts'),
        'portRcvPkts': (Int64(), 'count', 'none', 'portRcvPkts'),
        'involved_jobs': (String(8192), 'string', 'none', 'involved_jobs')
        }
        
    counters_infinibandstats_to_get = [
        'portXmitData',
        'portRcvData',
        'portXmitPkts',
        'portRcvPkts',
        'involved_jobs'
    ]

    _counters = []
        
    for c_name in counters_infinibandstats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_infinibandstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(infinibandstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, infinibandstats_backend):
        return infinibandstats_backend.get_infinibandstats()

    def __init__(self, infinibandstats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif infinibandstats_buffer is None:
            self._empty_fill()
        else:
            for name in InfinibandstatsCounters._counter_definitions:
                self._counter_values[name] = infinibandstats_buffer[name]
