import logging

LOG = logging.getLogger()

from .base import UInt64, BaseCounters


class LustrestatsCounters(BaseCounters):
    __metric_name__ = 'lustrestats_default'

    counters_lustrestats = {
        # 'key': ( offset,length, type, repr, acc )
        'lustre_nb_read': (UInt64(), 'count', 'none', 'lustre_nb_read'),
        'lustre_bytes_read': (UInt64(), 'bytes', 'none', 'lustre_bytes_read'),
        'lustre_nb_write': (UInt64(), 'count', 'none', 'lustre_nb_write'),
        'lustre_bytes_write': (UInt64(), 'bytes', 'none', 'lustre_bytes_write'),
        }
        
    counters_lustrestats_to_get = [
        'lustre_nb_read',
        'lustre_bytes_read',
        'lustre_nb_write',
        'lustre_bytes_write'
    ]

    _counters = []
        
    for c_name in counters_lustrestats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_lustrestats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(lustrestats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, lustrestats_backend):
        return lustrestats_backend.get_lustrestats()

    def __init__(self, lustrestats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif lustrestats_buffer is None:
            self._empty_fill()
        else:
            for name in LustrestatsCounters._counter_definitions:
                self._counter_values[name] = lustrestats_buffer[name]
