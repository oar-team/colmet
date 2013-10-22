
import time

from nose.tools import *

import colmet.metrics.taskstats_default as td
from colmet.metrics.base import get_counters_class

def test_get_counters_class():
    '''Test: import the taskstats_default metric class'''
    Counter = get_counters_class('taskstats_default')
    assert(Counter._get_metric_name() == 'taskstats_default')


def setup_metric():
    global counter
    global timestamp

    Counter = get_counters_class('taskstats_default')
    counter = Counter()

def test_counters_initialisation():
    '''Test: taskstats_metric initialization'''
    setup_metric()

