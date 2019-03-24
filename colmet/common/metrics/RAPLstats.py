import logging

LOG = logging.getLogger()

from .base import UInt64, BaseCounters


class RAPLstatsCounters(BaseCounters):
    __metric_name__ = 'RAPLstats_default'

    counters_RAPLstats = {
        # 'key': ( offset,length, type, repr, acc )
        'maxEnergyRangeUJ': (UInt64(), 'count', 'none', 'maxEnergyRangeUJ'),
        'energyUJ': (UInt64(), 'count', 'none', 'energyUJ')
        }
        
    counters_RAPLstats_to_get = [
        'maxEnergyRangeUJ',
        'energyUJ'
    ]

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
