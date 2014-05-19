import logging

LOG = logging.getLogger()

from .base import UInt64, UFloat, BaseCounters


class ProcstatsCounters(BaseCounters):
    __metric_name__ = 'procstats_default'

    counters_procstats = {
        # 'key': ( offset,length, type, repr, acc )
        'uptime_total': (UInt64(), 'sec', 'none', 'uptime.total'),
        'uptime_idle': (UInt64(), 'sec', 'none', 'uptime.idle'),
        'meminfo_memtotal': (UInt64(), 'kbytes', 'none', 'meminfo_memtotal'),
        'meminfo_memfree': (UInt64(), 'kbytes', 'none', 'meminfo_memfree'),
        'meminfo_buffers': (UInt64(), 'kbytes', 'none', 'meminfo_buffers'),
        'meminfo_cached': (UInt64(), 'kbytes', 'none', 'meminfo_cached'),
        'meminfo_swapcached': (UInt64(), 'kbytes', 'none', 'meminfo_swapcached'),
        'meminfo_active': (UInt64(), 'kbytes', 'none', 'meminfo_active'),
        'meminfo_inactive': (UInt64(), 'kbytes', 'none', 'meminfo_inactive'),
        'meminfo_unevictable': (UInt64(), 'kbytes', 'none', 'meminfo_unevictable'),
        'meminfo_mlocked': (UInt64(), 'kbytes', 'none', 'meminfo_mlocked'),
        'meminfo_swaptotal': (UInt64(), 'kbytes', 'none', 'meminfo_swaptotal'),
        'meminfo_swapfree': (UInt64(), 'kbytes', 'none', 'meminfo_swapfree'),
        'meminfo_dirty': (UInt64(), 'kbytes', 'none', 'meminfo_dirty'),
        'meminfo_writeback': (UInt64(), 'kbytes', 'none', 'meminfo_writeback'),
        'meminfo_anonpages': (UInt64(), 'kbytes', 'none', 'meminfo_anonpages'),
        'meminfo_mapped': (UInt64(), 'kbytes', 'none', 'meminfo_mapped'),
        'meminfo_shmem': (UInt64(), 'kbytes', 'none', 'meminfo_shmem'),
        'meminfo_slab': (UInt64(), 'kbytes', 'none', 'meminfo_slab'),
        'meminfo_sreclaimable': (UInt64(), 'kbytes', 'none', 'meminfo_sreclaimable'),
        'meminfo_sunreclaim': (UInt64(), 'kbytes', 'none', 'meminfo_sunreclaim'),
        'meminfo_kernelstack': (UInt64(), 'kbytes', 'none', 'meminfo_kernelstack'),
        'meminfo_pagetables': (UInt64(), 'kbytes', 'none', 'meminfo_pagetables'),
        'meminfo_nfs_unstable': (UInt64(), 'kbytes', 'none', 'meminfo_nfs_unstable'),
        'meminfo_bounce': (UInt64(), 'kbytes', 'none', 'meminfo_bounce'),
        'meminfo_writebacktmp': (UInt64(), 'kbytes', 'none', 'meminfo_writebacktmp'),
        'meminfo_commitlimit': (UInt64(), 'kbytes', 'none', 'meminfo_commitlimit'),
        'meminfo_committed_as': (UInt64(), 'kbytes', 'none', 'meminfo_committed_as'),
        'meminfo_vmalloctotal': (UInt64(), 'kbytes', 'none', 'meminfo_vmalloctotal'),
        'meminfo_vmallocused': (UInt64(), 'kbytes', 'none', 'meminfo_vmallocused'),
        'meminfo_vmallocchunk': (UInt64(), 'kbytes', 'none', 'meminfo_vmallocchunk'),
        'meminfo_hardwarecorrupted': (UInt64(), 'kbytes', 'none', 'meminfo_hardwarecorrupted'),
        'meminfo_anonhugepages': (UInt64(), 'kbytes', 'none', 'meminfo_anonhugepages'),
        'meminfo_hugepages_total': (UInt64(), 'count', 'none', 'meminfo_hugepages_total'),
        'meminfo_hugepages_free': (UInt64(), 'count', 'none', 'meminfo_hugepages_free'),
        'meminfo_hugepages_rsvd': (UInt64(), 'count', 'none', 'meminfo_hugepages_rsvd'),
        'meminfo_hugepages_surp': (UInt64(), 'count', 'none', 'meminfo_hugepages_surp'),
        'meminfo_hugepagesize': (UInt64(), 'count', 'none', 'meminfo_hugepagesize'),
        'meminfo_directmap4k': (UInt64(), 'kbytes', 'none', 'meminfo_directmap4k'),
        'meminfo_directmap2m': (UInt64(), 'kbytes', 'none', 'meminfo_directmap2m'),
        'vmstat_pgpgin': (UInt64(), 'count', 'none', 'vmstat_pgpgin'),
        'vmstat_pgpgout': (UInt64(), 'count', 'none', 'vmstat_pgpgout'),
        'vmstat_pswpin': (UInt64(), 'count', 'none', 'vmstat_pswpin'),
        'vmstat_pswpout': (UInt64(), 'count', 'none', 'vmstat_pswpout'),
        'vmstat_pgfault': (UInt64(), 'count', 'none', 'vmstat_pgfault'),
        'vmstat_pgmajfault': (UInt64(), 'count', 'none', 'vmstat_pgmajfault'),
        'stat_cpu_user': (UInt64(), 'n/a', 'none', 'stat_cpu_user'),
        'stat_cpu_nice': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_system': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_idle': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_iowait': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_irq': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_softirq': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_guest': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_cpu_guest_nice': (UInt64(), 'n/a', 'none', 'stat_cpu_nice'),
        'stat_intr': (UInt64(), 'n/a', 'none', 'stat_intr'),
        'stat_ctxt': (UInt64(), 'n/a', 'none', 'stat_ctxt'),
        'stat_processes': (UInt64(), 'n/a', 'none', 'stat_processes'),
        'stat_procs_blocked': (UInt64(), 'n/a', 'none', 'stat_procs_blocked'),
        'loadavg_1min': (UFloat(), 'n/a', 'none', 'loadavg_1min'),
        'loadavg_5min': (UFloat(), 'n/a', 'none', 'loadavg_5min'),
        'loadavg_15min': (UFloat(), 'n/a', 'none', 'loadavg_15min'),
        'loadavg_runnable': (UFloat(), 'n/a', 'none', 'loadavg_runnable'),
        'loadavg_total_threads': (UFloat(), 'n/a', 'none', 'loadavg_total_threads')
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
        # 'sys_numa_zoneallocs',
        # 'sys_numa_zoneallocs',
        # 'sys_numa_foreign_allocs',
        # 'sys_numa_allocation',
        # 'sys_numa_allocation',
        # 'sys_numa_interleave',
    ]

    _counters = []
    for c_name in counters_procstats_to_get:
        (c_type, c_repr, c_acc, c_descr) = counters_procstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return  cls(procstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, procstats_backend):
        return procstats_backend.get_procstats()

    def __init__(self, procstats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif procstats_buffer is None:
            self._empty_fill()
        else:
            for name in ProcstatsCounters._counter_definitions:
                self._counter_values[name] = procstats_buffer[name]
