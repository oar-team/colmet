# -*- coding: utf-8 -*-
"""
Testing the base metric class
"""
import pytest

from colmet.common.metrics.base import (UInt8, UInt16, UInt32, UInt64, String,
                                        BaseCounters, CounterAlreadyExistError)


def test_basic_types():
    assert UInt8().length == 2
    assert UInt16().length == 2
    assert UInt32().length == 4
    assert UInt64().length == 8
    for i in [1, 5, 0, 100]:
        assert String(i).length == i


class MyCounters(BaseCounters):
    _headers = [
        ('project', String(16), 'string')
    ]

    _counters = [
        ('speed', UInt64(), 'count', 'add', 'Speed')
    ]


@pytest.fixture(scope="function")
def mycounters(request, monkeypatch):
    m = MyCounters()
    m.job_id = 42
    m.timestamp = 0
    m.hostname = 'localhost'
    return m


def test_register_header():
    '''Testing registering header'''
    assert 'project' in MyCounters._header_definitions

    (h_type, h_repr, h_index, h_offset) = MyCounters._header_definitions[
        'project']

    assert h_type == String(16)
    assert h_repr == 'string'
    assert h_offset is not None
    assert h_index is not None


def test_register_counters():
    '''Testing registering counter'''
    assert 'speed' in MyCounters._counter_definitions

    class MyCounters2(MyCounters):

        _counters = [
            ('speed2', UInt32(), 'count', 'add', 'Speed2')
        ]

    assert 'speed2' in MyCounters2._counter_definitions

    (c_type, c_repr, c_acc_fn, c_descr, c_index,
     c_offset) = MyCounters2._counter_definitions['speed2']

    assert c_type == UInt32()
    assert c_repr == 'count'
    assert c_acc_fn == 'add'
    assert c_descr == 'Speed2'
    assert c_offset is not None
    assert c_index is not None


def test_counter_assignment(mycounters):
    '''Testing basic counters get/set'''
    mycounters.speed = 120
    assert(mycounters.speed == 120)
    assert(mycounters._get_counter('speed') == 120)


def test_counter_packed_assignment(mycounters):
    '''Testing packed/unpacked counters get/set'''
    mycounters.project = 'speedcontrol'
    mycounters.speed = 0
    mycounters.pack()
    assert(mycounters.speed == 0)
    mycounters.speed = 120
    assert(mycounters.speed == 120)
    mycounters.unpack()
    assert(mycounters.speed == 120)


def test_failure_if_regitering_an_existing_counter():
    '''Registering an existing counter should fail'''
    with pytest.raises(CounterAlreadyExistError):
        class MyCounters2(MyCounters):
            _counters = [
                ('speed', UInt64(), 'count', 'add', 'Speed')
            ]


def test_failure_if_regitering_an_existing_headerr():
    '''Registering an existing counter should fail'''
    with pytest.raises(CounterAlreadyExistError):
        class MyCounters2(MyCounters):
            _headers = [
                ('job_id', UInt64(), 'string')
            ]


def test_normalize():
    '''Testing formating value (Normalization)'''
    val = BaseCounters._normalize(1, 1000, 10000, ['', 'K', 'G'])
    assert val == "1"
    val = BaseCounters._normalize(1000, 1000, 10000, ['', 'K', 'G'])
    assert val == "1000"
    val = BaseCounters._normalize(100000, 1000, 10000, ['', 'K', 'G'])
    assert val == "100K"


def test_failure_if_deriving_counters_from_multiple_class():
    class MyCounters2(MyCounters):
        pass

    with pytest.raises(TypeError):
        class MyCounters3(MyCounters, MyCounters2):
            pass
