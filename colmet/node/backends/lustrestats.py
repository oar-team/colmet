import os
import re

import glob

from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.lustrestats import LustrestatsCounters


class LustrestatsBackend(InputBaseBackend):
    __backend_name__ = "lustrestats"

    def open(self):
        self.lustrestats = LustreStats(self.options)
        # job with id equal to 0 is the fictive job to gather nodes' monitoring
        # measures
        self.job_0 = Job(self, 0, self.options)

    def close(self):
        pass

    def get_lustrestats(self):
        counters = self.lustrestats.get_stats()
        return counters

    def get_counters_class(self):
        return LustrestatsCounters

    def pull(self):
        self.job_0.update_stats()
        return self.job_0.get_stats()


class LustreStats(object):
    '''
    Read counters from all mounted lustre fs
    from the file stats under the directories:
  
    /proc/fs/lustre/llite/lustre-xxxx/stats

    From the file stat we use 2 entries:

    read_bytes          17996 samples [bytes] 0 4194304 30994606834
    write_bytes         9007 samples [bytes] 2 4194304 31008331389

    First number = number of times (samples) the OST has handled a read or write.
    Second number = the minimum read/write size
    Third number = maximum read/write size
    Fourth = sum of all the read/write requests in bytes, the quantity of data read/written.
    '''

    def __init__(self, option):
        self.options = option

    def get_stats(self):

        lustre_nb_read = 0
        lustre_bytes_read = 0
        lustre_nb_write = 0
        lustre_bytes_write = 0
        
        for stats_file_name in glob.glob('/proc/fs/lustre/llite/lustre-*/stats'):
            with open(stats_file_name) as stats_file:
                for line in stats_file:
                    if re.match('read_bytes', line):
                        values = line.split()
                        lustre_nb_read += int(values[1])
                        lustre_bytes_read += int(values[-1])
                    if re.match('write_bytes', line):
                        values = line.split()
                        lustre_nb_write += int(values[1])
                        lustre_bytes_write += int(values[-1])
                        
        lustrestats_data = {'lustre_nb_read': lustre_nb_read, 'lustre_bytes_read': lustre_bytes_read,
                            'lustre_nb_write': lustre_nb_write, 'lustre_bytes_write': lustre_bytes_write
        }
                        
        return LustrestatsCounters(lustrestats_buffer=lustrestats_data)
