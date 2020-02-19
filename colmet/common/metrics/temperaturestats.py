import logging

LOG = logging.getLogger()

from .base import UInt64, Int64, BaseCounters


class TemperaturestatsCounters(BaseCounters):
    __metric_name__ = 'temperaturestats_default'

    counters_temperaturestats = {
        # 'key': ( offset,length, type, repr, acc )
        'counter_1': (Int64(), 'celsius', 'none', 'counter1'),
        'counter_2': (Int64(), 'celsius', 'none', 'counter2'),
        'counter_3': (Int64(), 'celsius', 'none', 'counter3'),
        'counter_4': (Int64(), 'celsius', 'none', 'counter4'),
        'counter_5': (Int64(), 'celsius', 'none', 'counter5'),
        'counter_6': (Int64(), 'celsius', 'none', 'counter6'),

    }

    counters_temperaturestats_to_get = [
        'counter_1',
        'counter_2',
        'counter_3',
        'counter_4',
        'counter_5',
        'counter_6',
    ]

    _counters = []

    for c_name in counters_temperaturestats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_temperaturestats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(temperaturestats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, temperaturestats_backend):
        return temperaturestats_backend.get_temperaturestats()

    def __init__(self, temperaturestats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif temperaturestats_buffer is None:
            self._empty_fill()
        else:
            for name in TemperaturestatsCounters._counter_definitions:
                self._counter_values[name] = temperaturestats_buffer[name]
