import struct
import logging
import os

LOG = logging.getLogger()

from colmet.metrics.base import UInt64, UFloat, String, BaseCounters

def get_counters_class():
    return Counters

def get_procstats_class():
    return Counters
  
class Counters(BaseCounters):
    counters_procstats = {
        # 'key' : ( offset,length, type, repr, acc )
        'uptime_total' :                ( UInt64(),'sec', 'none', 'uptime.total'),
        'uptime_idle'  :                ( UInt64(),'sec', 'none', 'uptime.idle'),
        'meminfo_memtotal' :            ( UInt64(),'kbytes', 'none', 'meminfo_memtotal'),
        'meminfo_memfree' :                ( UInt64(),'kbytes', 'none', 'meminfo_memfree'),
        'meminfo_buffers' :                ( UInt64(),'kbytes', 'none', 'meminfo_buffers'),
        'meminfo_cached' :                ( UInt64(),'kbytes', 'none', 'meminfo_cached'),
        'meminfo_swapcached' :            ( UInt64(),'kbytes', 'none', 'meminfo_swapcached'),
        'meminfo_active' :                ( UInt64(),'kbytes', 'none', 'meminfo_active'),
        'meminfo_inactive' :            ( UInt64(),'kbytes', 'none', 'meminfo_inactive'),
        'meminfo_unevictable' :            ( UInt64(),'kbytes', 'none', 'meminfo_unevictable'),
        'meminfo_mlocked' :                ( UInt64(),'kbytes', 'none', 'meminfo_mlocked'),
        'meminfo_swaptotal' :            ( UInt64(),'kbytes', 'none', 'meminfo_swaptotal'),
        'meminfo_swapfree' :            ( UInt64(),'kbytes', 'none', 'meminfo_swapfree'),
        'meminfo_dirty' :                ( UInt64(),'kbytes', 'none', 'meminfo_dirty'),
        'meminfo_writeback' :            ( UInt64(),'kbytes', 'none', 'meminfo_writeback'),
        'meminfo_anonpages' :            ( UInt64(),'kbytes', 'none', 'meminfo_anonpages'),
        'meminfo_mapped' :                ( UInt64(),'kbytes', 'none', 'meminfo_mapped'),
        'meminfo_shmem' :                ( UInt64(),'kbytes', 'none', 'meminfo_shmem'),
        'meminfo_slab' :                ( UInt64(),'kbytes', 'none', 'meminfo_slab'),
        'meminfo_sreclaimable' :        ( UInt64(),'kbytes', 'none', 'meminfo_sreclaimable'),
        'meminfo_sunreclaim' :            ( UInt64(),'kbytes', 'none', 'meminfo_sunreclaim'),
        'meminfo_kernelstack' :            ( UInt64(),'kbytes', 'none', 'meminfo_kernelstack'),
        'meminfo_pagetables' :            ( UInt64(),'kbytes', 'none', 'meminfo_pagetables'),
        'meminfo_nfs_unstable' :        ( UInt64(),'kbytes', 'none', 'meminfo_nfs_unstable'),
        'meminfo_bounce' :                ( UInt64(),'kbytes', 'none', 'meminfo_bounce'),
        'meminfo_writebacktmp' :        ( UInt64(),'kbytes', 'none', 'meminfo_writebacktmp'),
        'meminfo_commitlimit' :            ( UInt64(),'kbytes', 'none', 'meminfo_commitlimit'),
        'meminfo_committed_as' :        ( UInt64(),'kbytes', 'none', 'meminfo_committed_as'),
        'meminfo_vmalloctotal' :        ( UInt64(),'kbytes', 'none', 'meminfo_vmalloctotal'),
        'meminfo_vmallocused' :            ( UInt64(),'kbytes', 'none', 'meminfo_vmallocused'),
        'meminfo_vmallocchunk' :        ( UInt64(),'kbytes', 'none', 'meminfo_vmallocchunk'),
        'meminfo_hardwarecorrupted' :    ( UInt64(),'kbytes', 'none', 'meminfo_hardwarecorrupted'),
        'meminfo_anonhugepages' :        ( UInt64(),'kbytes', 'none', 'meminfo_anonhugepages'),
        'meminfo_hugepages_total' :        ( UInt64(),'count', 'none', 'meminfo_hugepages_total'),
        'meminfo_hugepages_free' :        ( UInt64(),'count', 'none', 'meminfo_hugepages_free'),
        'meminfo_hugepages_rsvd' :        ( UInt64(),'count', 'none', 'meminfo_hugepages_rsvd'),
        'meminfo_hugepages_surp' :        ( UInt64(),'count', 'none', 'meminfo_hugepages_surp'),
        'meminfo_hugepagesize' :        ( UInt64(),'count', 'none', 'meminfo_hugepagesize'),
        'meminfo_directmap4k' :            ( UInt64(),'kbytes', 'none', 'meminfo_directmap4k'),
        'meminfo_directmap2m' :            ( UInt64(),'kbytes', 'none', 'meminfo_directmap2m'),
        'vmstat_pgpgin' :                ( UInt64(),'count', 'none', 'vmstat_pgpgin'),
        'vmstat_pgpgout' :                ( UInt64(),'count', 'none', 'vmstat_pgpgout'),
        'vmstat_pswpin' :                ( UInt64(),'count', 'none', 'vmstat_pswpin'),
        'vmstat_pswpout' :                ( UInt64(),'count', 'none', 'vmstat_pswpout'),
        'vmstat_pgfault' :                ( UInt64(),'count', 'none', 'vmstat_pgfault'),
        'vmstat_pgmajfault' :            ( UInt64(),'count', 'none', 'vmstat_pgmajfault'),
        'stat_cpu_user' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_user'),
        'stat_cpu_nice' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_system' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_idle' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_iowait' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_irq' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_softirq' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_guest' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_guest_nice' :                    ( UInt64(),'n/a', 'none', 'stat_cpu_nice'),
        'stat_intr' :                    ( UInt64(),'n/a', 'none', 'stat_intr'),
        'stat_ctxt' :                    ( UInt64(),'n/a', 'none', 'stat_ctxt'),
        'stat_processes' :                ( UInt64(),'n/a', 'none', 'stat_processes'),
        'stat_procs_blocked' :            ( UInt64(),'n/a', 'none', 'stat_procs_blocked'),
        'loadavg_1min' :                ( UFloat(),'n/a', 'none', 'loadavg_1min'),
        'loadavg_5min' :                ( UFloat(),'n/a', 'none', 'loadavg_5min'),
        'loadavg_15min' :                ( UFloat(),'n/a', 'none', 'loadavg_15min'),
        'loadavg_runnable' :            ( UFloat(),'n/a', 'none', 'loadavg_runnable'),
        'loadavg_total_threads' :        ( UFloat(),'n/a', 'none', 'loadavg_total_threads')
    }
 
    counters_procstats_to_get = [
        'uptime_total',
        'uptime_idle',
        'meminfo_memtotal',
        'meminfo_memfree',
        'meminfo_buffers',
        'meminfo_cached',
        'meminfo_swapcached',
        'meminfo_active',
        'meminfo_inactive',
        'meminfo_unevictable',
        'meminfo_mlocked',
        'meminfo_swaptotal',
        'meminfo_swapfree',
        'meminfo_dirty',
        'meminfo_writeback',
        'meminfo_anonpages',
        'meminfo_mapped',
        'meminfo_shmem',
        'meminfo_slab',
        'meminfo_sreclaimable',
        'meminfo_sunreclaim',
        'meminfo_kernelstack',
        'meminfo_pagetables',
        'meminfo_nfs_unstable',
        'meminfo_bounce',
        'meminfo_writebacktmp',
        'meminfo_commitlimit',
        'meminfo_committed_as',
        'meminfo_vmalloctotal',
        'meminfo_vmallocused',
        'meminfo_vmallocchunk',
        'meminfo_hardwarecorrupted',
        'meminfo_anonhugepages',
        'meminfo_hugepages_total',
        'meminfo_hugepages_free',
        'meminfo_hugepages_rsvd',
        'meminfo_hugepages_surp',
        'meminfo_hugepagesize',
        'meminfo_directmap4k',
        'meminfo_directmap2m',
        'vmstat_pgpgin',
        'vmstat_pgpgout',
        'vmstat_pswpin',
        'vmstat_pswpout',
        'vmstat_pgfault',
        'vmstat_pgmajfault',
        'stat_cpu_user',
        'stat_cpu_nice',
        'stat_cpu_system',
        'stat_cpu_idle',
        'stat_cpu_iowait',
        'stat_cpu_irq',
        'stat_cpu_softirq',
        'stat_cpu_guest',
        'stat_cpu_guest_nice',
        'stat_intr',
        'stat_ctxt',
        'stat_processes',
        'stat_procs_blocked',
        'loadavg_1min',
        'loadavg_5min',
        'loadavg_15min',
        'loadavg_runnable',
        'loadavg_total_threads'
#        'sys_numa_zoneallocs',
#        'sys_numa_zoneallocs',
#        'sys_numa_foreign_allocs',
#        'sys_numa_allocation',
#        'sys_numa_allocation',
#        'sys_numa_interleave',
    ]

    _counters = []
    for c_name in counters_procstats_to_get:
        ( c_type, c_repr, c_acc,c_descr) = counters_procstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return  cls(procstats_buffer = None, raw= None)

    @classmethod
    def fetch(cls, procstats_backend):
        return procstats_backend.get_procstats()

    @classmethod
    def _get_metric_name(cls):
        return 'procstats_default'

    def __init__(self, procstats_buffer = None, raw = None):
        BaseCounters.__init__(self, raw=raw)
        if raw != None:
            pass
        elif procstats_buffer == None:
            self._empty_fill()
        else:
            print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            for name in Counters._counter_definitions:
                self._counter_values[name] = procstats_buffer[name]

def get_hdf5_class():
    try:
        import tables
        class HDF5Counters(object): 
            class HDF5TableDescription(tables.IsDescription):

                metric_backend = tables.StringCol(255)
                timestamp = tables.Int64Col(dflt = -1)
                hostname = tables.StringCol(255)
                job_id   = tables.Int64Col(dflt = -1)

                uptime_total = tables.Int64Col(dflt = -1)
                uptime_idle  = tables.Int64Col(dflt = -1)

                meminfo_memtotal = tables.Int64Col(dflt = -1)
                meminfo_memfree = tables.Int64Col(dflt = -1)
                meminfo_buffers = tables.Int64Col(dflt = -1)
                meminfo_cached = tables.Int64Col(dflt = -1)
                meminfo_swapcached = tables.Int64Col(dflt = -1)
                meminfo_active = tables.Int64Col(dflt = -1)
                meminfo_inactive = tables.Int64Col(dflt = -1)
                meminfo_unevictable = tables.Int64Col(dflt = -1)
                meminfo_mlocked = tables.Int64Col(dflt = -1)
                meminfo_swaptotal = tables.Int64Col(dflt = -1)
                meminfo_swapfree = tables.Int64Col(dflt = -1)
                meminfo_dirty = tables.Int64Col(dflt = -1)
                meminfo_writeback = tables.Int64Col(dflt = -1)
                meminfo_anonpages = tables.Int64Col(dflt = -1)
                meminfo_mapped = tables.Int64Col(dflt = -1)
                meminfo_shmem = tables.Int64Col(dflt = -1)
                meminfo_slab = tables.Int64Col(dflt = -1)
                meminfo_sreclaimable = tables.Int64Col(dflt = -1)
                meminfo_sunreclaim = tables.Int64Col(dflt = -1)
                meminfo_kernelstack = tables.Int64Col(dflt = -1)
                meminfo_pagetables = tables.Int64Col(dflt = -1)
                meminfo_nfs_unstable = tables.Int64Col(dflt = -1)
                meminfo_bounce = tables.Int64Col(dflt = -1)
                meminfo_writebacktmp = tables.Int64Col(dflt = -1)
                meminfo_commitlimit = tables.Int64Col(dflt = -1)
                meminfo_committed_as = tables.Int64Col(dflt = -1)
                meminfo_vmalloctotal = tables.Int64Col(dflt = -1)
                meminfo_vmallocused = tables.Int64Col(dflt = -1)
                meminfo_vmallocchunk = tables.Int64Col(dflt = -1)
                meminfo_hardwarecorrupted = tables.Int64Col(dflt = -1)
                meminfo_anonhugepages = tables.Int64Col(dflt = -1)
                meminfo_hugepages_total = tables.Int64Col(dflt = -1)
                meminfo_hugepages_free = tables.Int64Col(dflt = -1)
                meminfo_hugepages_rsvd = tables.Int64Col(dflt = -1)
                meminfo_hugepages_surp = tables.Int64Col(dflt = -1)
                meminfo_hugepagesize = tables.Int64Col(dflt = -1)
                meminfo_directmap4k = tables.Int64Col(dflt = -1)
                meminfo_directmap2m = tables.Int64Col(dflt = -1)

                vmstat_pgpgin = tables.Int64Col(dflt = -1)
                vmstat_pgpgout = tables.Int64Col(dflt = -1)
                vmstat_pswpin = tables.Int64Col(dflt = -1)
                vmstat_pswpout = tables.Int64Col(dflt = -1)
                vmstat_pgfault = tables.Int64Col(dflt = -1)
                vmstat_pgmajfault = tables.Int64Col(dflt = -1)

                stat_cpu_user = tables.Int64Col(dflt = -1)
                stat_cpu_nice = tables.Int64Col(dflt = -1)
                stat_cpu_system = tables.Int64Col(dflt = -1)
                stat_cpu_idle = tables.Int64Col(dflt = -1)
                stat_cpu_iowait = tables.Int64Col(dflt = -1)
                stat_cpu_irq = tables.Int64Col(dflt = -1)
                stat_cpu_softirq = tables.Int64Col(dflt = -1)
                stat_cpu_guest = tables.Int64Col(dflt = -1)
                stat_cpu_guest_nice = tables.Int64Col(dflt = -1)

                stat_intr = tables.Int64Col(dflt = -1)
                stat_ctxt = tables.Int64Col(dflt = -1)
                stat_processes = tables.Int64Col(dflt = -1)
                stat_procs_blocked = tables.Int64Col(dflt = -1)

                loadavg_1min = tables.Float32Col(dflt = -1)
                loadavg_5min = tables.Float32Col(dflt = -1)
                loadavg_15min = tables.Float32Col(dflt = -1)
                loadavg_runnable = tables.Float32Col(dflt = -1)
                loadavg_total_threads = tables.Float32Col(dflt = -1)

#                sys_numa_zoneallocs = tables.Int64Col(dflt = -1)
#                sys_numa_zoneallocs = tables.Int64Col(dflt = -1)
#                sys_numa_foreign_allocs = tables.Int64Col(dflt = -1)
#                sys_numa_allocation = tables.Int64Col(dflt = -1)
#                sys_numa_allocation = tables.Int64Col(dflt = -1)
#                sys_numa_interleave = tables.Int64Col(dflt = -1)

            @classmethod
            def get_table_description(cls):
                return cls.HDF5TableDescription
           
            @classmethod
            def to_counters(cls,row):
                counters = Counters()
                for key in Counters._header_definitions.keys():
                    counters._set_header(key, row[key])
                
                for key in Counters._counter_definitions.keys():
                    counters._set_counter(key, row[key])
                return counters
            
            @classmethod
            def to_row(cls,row,counters):
                for key in Counters._header_definitions.keys():
                    row[key] = counters._get_header(key)
                for key in Counters._counter_definitions.keys():
                    row[key] = counters._get_counter(key)

        return HDF5Counters

    except ImportError:
        raise UnableToFindLibraryError('tables')

