

from colmet.metrics.base import get_counters_class


def test_get_counters_class():
    '''Test: import the procstats_default metric class'''
    counter_class = get_counters_class('procstats_default')
    assert counter_class._get_metric_name() == 'procstats_default'


def setup_metric():
    global counter
    global timestamp

    counter_class = get_counters_class('procstats_default')
    counter = counter_class()


def test_counters_initialisation():
    '''Test: procstats_metric initialization'''
    setup_metric()
