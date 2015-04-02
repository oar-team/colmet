
from colmet.metrics.base import get_counters_class


def test_get_counters_class():
    '''Test: import the taskstats_default metric class'''
    counter_class = get_counters_class('taskstats_default')
    assert(counter_class._get_metric_name() == 'taskstats_default')


def setup_metric():
    global counter
    global timestamp

    counter_class = get_counters_class('taskstats_default')
    counter = counter_class()


def test_counters_initialisation():
    '''Test: taskstats_metric initialization'''
    setup_metric()
