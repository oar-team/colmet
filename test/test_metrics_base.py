"""
Testing the base metric class
"""
from nose.tools import *

from colmet.metrics.base import *

def test_basic_types():
    assert(UInt8().length == 2)
    assert(UInt16().length == 2)
    assert(UInt32().length == 4)
    assert(UInt64().length == 8)
    for i in [1,5,0,100]:
        assert( String(i).length==i)

def test_basecounters_packing_unpacking():
    import os
    import ctypes

    raw = os.urandom(BaseCounters._fmt_length)

    m = BaseCounters()

    m.unpack_from(raw,0)

    raw2=ctypes.create_string_buffer(BaseCounters._fmt_length)

    m.pack_into(raw2,0)

    assert raw2.raw == raw


class MyCounters(BaseCounters):
    _headers = [
        ('project',String(16),'string')
    ]

    _counters = [
        ('speed',UInt64(),'count','add','Speed')
    ]

m = None

def setup_mycounters():
    global m
    m = MyCounters()
    m.job_id = 42
    m.timestamp = 0
    m.hostname = 'localhost'

def teardown_mycounters():
    global m
    del m

def test_register_header():
    '''Testing registering header'''
    assert 'project' in  MyCounters._header_definitions

    (h_type,h_repr,h_index,h_offset) = MyCounters._header_definitions['project']

    assert h_type == String(16)
    assert h_repr == 'string'
    assert h_offset != None
    assert h_index != None

def test_register_counters():
    '''Testing registering counter'''
    assert 'speed' in  MyCounters._counter_definitions

    class MyCounters2(MyCounters):

        _counters = [
            ('speed2',UInt32(),'count','add','Speed2')
        ]

    assert 'speed2' in  MyCounters2._counter_definitions

    (c_type,c_repr,c_acc_fn, c_descr, c_index,c_offset) = MyCounters2._counter_definitions['speed2']

    assert c_type == UInt32()
    assert c_repr == 'count'
    assert c_acc_fn == 'add'
    assert c_descr == 'Speed2'
    assert c_offset != None
    assert c_index != None

@with_setup(setup_mycounters,teardown_mycounters)
def test_counter_assignment():
    '''Testing basic counters get/set'''
    m.speed = 120
    assert(m.speed == 120)
    assert(m._get_counter('speed') == 120)

@with_setup(setup_mycounters,teardown_mycounters)
def test_counter_packed_assignment():
    '''Testing packed/unpacked counters get/set'''
    m.project = 'speedcontrol'
    m.speed = 0
    m.pack()
    assert(m.speed == 0)
    m.speed = 120
    assert(m.speed == 120)
    m.unpack()
    assert(m.speed == 120)

@raises(CounterAlreadyExistError)
def test_failure_if_regitering_an_existing_counter():
    '''Registering an existing counter should fail'''
    class MyCounters2(MyCounters):
        _counters = [
            ('speed',UInt64(),'count','add','Speed')
        ]

@raises(CounterAlreadyExistError)
def test_failure_if_regitering_an_existing_headerr():
    '''Registering an existing counter should fail'''
    class MyCounters2(MyCounters):
        _headers = [
            ('job_id',UInt64(),'string')
        ]


def test_normalize():
    '''Testing formating value (Normalization)'''
    val = BaseCounters._normalize(1,1000,10000,['','K','G'])
    assert val == "1"
    val = BaseCounters._normalize(1000,1000,10000,['','K','G'])
    assert val == "1000"
    val = BaseCounters._normalize(100000,1000,10000,['','K','G'])
    assert val == "100K"

@raises(TypeError)
def test_failure_if_deriving_counters_from_multiple_class():
    class MyCounters2(MyCounters):
        pass

    class MyCounters3(MyCounters, MyCounters2):
        pass
