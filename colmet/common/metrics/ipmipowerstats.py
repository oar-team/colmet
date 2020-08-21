import logging

LOG = logging.getLogger()

from .base import UInt64, Int64, BaseCounters, String


class IpmipowerstatsCounters(BaseCounters):
    __metric_name__ = 'ipmipowerstats_default'

    counters_ipmipowerstats = {
        # 'key': ( offset,length, type, repr, acc )
        'average_power_consumption': (Int64(), 'count', 'none', 'average_power_consumption'),
        'involved_jobs': (String(8192), 'string', 'none', 'involved_jobs')
        }
        
    counters_ipmipowerstats_to_get = [
        'average_power_consumption',
        'involved_jobs'
    ]

    _counters = []
        
    for c_name in counters_ipmipowerstats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_ipmipowerstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(ipmipowerstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, ipmipowerstats_backend):
        return ipmipowerstats_backend.get_ipmipowerstats()

    def __init__(self, ipmipowerstats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif ipmipowerstats_buffer is None:
            self._empty_fill()
        else:
            for name in IpmipowerstatsCounters._counter_definitions:
                self._counter_values[name] = ipmipowerstats_buffer[name]
