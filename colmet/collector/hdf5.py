'''
stdout backend : print information to stdout
'''
import logging
import os

from colmet.common.metrics import get_counters_class
from colmet.common.backends.base import OutputBaseBackend
import tables


LOG = logging.getLogger()

HDF5_BACKEND_VERSION = 2


class HDF5TaskstatsCounters(object):
    Counters = get_counters_class("taskstats_default")

    class HDF5TableDescription(tables.IsDescription):

        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)

        cpu_count = tables.Int64Col(dflt=-1)
        cpu_delay_total = tables.Int64Col(dflt=-1)
        blkio_count = tables.Int64Col(dflt=-1)
        blkio_delay_total = tables.Int64Col(dflt=-1)
        swapin_count = tables.Int64Col(dflt=-1)
        swapin_delay_total = tables.Int64Col(dflt=-1)
        cpu_run_real_total = tables.Int64Col(dflt=-1)
        cpu_run_virtual_total = tables.Int64Col(dflt=-1)
        ac_btime = tables.Int64Col(dflt=-1)
        ac_etime = tables.Int64Col(dflt=-1)
        ac_utime = tables.Int64Col(dflt=-1)
        ac_stime = tables.Int64Col(dflt=-1)
        ac_minflt = tables.Int64Col(dflt=-1)
        ac_majflt = tables.Int64Col(dflt=-1)
        coremem = tables.Int64Col(dflt=-1)
        virtmem = tables.Int64Col(dflt=-1)
        read_char = tables.Int64Col(dflt=-1)
        write_char = tables.Int64Col(dflt=-1)
        read_syscalls = tables.Int64Col(dflt=-1)
        write_syscalls = tables.Int64Col(dflt=-1)
        read_bytes = tables.Int64Col(dflt=-1)
        write_bytes = tables.Int64Col(dflt=-1)
        cancelled_write_bytes = tables.Int64Col(dflt=-1)
        nvcsw = tables.Int64Col(dflt=-1)
        nivcsw = tables.Int64Col(dflt=-1)
        ac_utimescaled = tables.Int64Col(dflt=-1)
        ac_stimescaled = tables.Int64Col(dflt=-1)
        cpu_scaled_run_real_total = tables.Int64Col(dflt=-1)
        freepages_count = tables.Int64Col(dflt=-1)
        freepages_delay_total = tables.Int64Col(dflt=-1)

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class HDF5ProcstatsCounters(object):
    Counters = get_counters_class("procstats_default")

    class HDF5TableDescription(tables.IsDescription):

        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)

        uptime_total = tables.Int64Col(dflt=-1)
        uptime_idle = tables.Int64Col(dflt=-1)

        meminfo_memtotal = tables.Int64Col(dflt=-1)
        meminfo_memfree = tables.Int64Col(dflt=-1)
        meminfo_buffers = tables.Int64Col(dflt=-1)
        meminfo_cached = tables.Int64Col(dflt=-1)
        meminfo_swapcached = tables.Int64Col(dflt=-1)
        meminfo_active = tables.Int64Col(dflt=-1)
        meminfo_inactive = tables.Int64Col(dflt=-1)
        meminfo_unevictable = tables.Int64Col(dflt=-1)
        meminfo_mlocked = tables.Int64Col(dflt=-1)
        meminfo_swaptotal = tables.Int64Col(dflt=-1)
        meminfo_swapfree = tables.Int64Col(dflt=-1)
        meminfo_dirty = tables.Int64Col(dflt=-1)
        meminfo_writeback = tables.Int64Col(dflt=-1)
        meminfo_anonpages = tables.Int64Col(dflt=-1)
        meminfo_mapped = tables.Int64Col(dflt=-1)
        meminfo_shmem = tables.Int64Col(dflt=-1)
        meminfo_slab = tables.Int64Col(dflt=-1)
        meminfo_sreclaimable = tables.Int64Col(dflt=-1)
        meminfo_sunreclaim = tables.Int64Col(dflt=-1)
        meminfo_kernelstack = tables.Int64Col(dflt=-1)
        meminfo_pagetables = tables.Int64Col(dflt=-1)
        meminfo_nfs_unstable = tables.Int64Col(dflt=-1)
        meminfo_bounce = tables.Int64Col(dflt=-1)
        meminfo_writebacktmp = tables.Int64Col(dflt=-1)
        meminfo_commitlimit = tables.Int64Col(dflt=-1)
        meminfo_committed_as = tables.Int64Col(dflt=-1)
        meminfo_vmalloctotal = tables.Int64Col(dflt=-1)
        meminfo_vmallocused = tables.Int64Col(dflt=-1)
        meminfo_vmallocchunk = tables.Int64Col(dflt=-1)
        meminfo_hardwarecorrupted = tables.Int64Col(dflt=-1)
        meminfo_anonhugepages = tables.Int64Col(dflt=-1)
        meminfo_hugepages_total = tables.Int64Col(dflt=-1)
        meminfo_hugepages_free = tables.Int64Col(dflt=-1)
        meminfo_hugepages_rsvd = tables.Int64Col(dflt=-1)
        meminfo_hugepages_surp = tables.Int64Col(dflt=-1)
        meminfo_hugepagesize = tables.Int64Col(dflt=-1)
        meminfo_directmap4k = tables.Int64Col(dflt=-1)
        meminfo_directmap2m = tables.Int64Col(dflt=-1)

        vmstat_pgpgin = tables.Int64Col(dflt=-1)
        vmstat_pgpgout = tables.Int64Col(dflt=-1)
        vmstat_pswpin = tables.Int64Col(dflt=-1)
        vmstat_pswpout = tables.Int64Col(dflt=-1)
        vmstat_pgfault = tables.Int64Col(dflt=-1)
        vmstat_pgmajfault = tables.Int64Col(dflt=-1)

        stat_cpu_user = tables.Int64Col(dflt=-1)
        stat_cpu_nice = tables.Int64Col(dflt=-1)
        stat_cpu_system = tables.Int64Col(dflt=-1)
        stat_cpu_idle = tables.Int64Col(dflt=-1)
        stat_cpu_iowait = tables.Int64Col(dflt=-1)
        stat_cpu_irq = tables.Int64Col(dflt=-1)
        stat_cpu_softirq = tables.Int64Col(dflt=-1)
        stat_cpu_guest = tables.Int64Col(dflt=-1)
        stat_cpu_guest_nice = tables.Int64Col(dflt=-1)

        stat_intr = tables.Int64Col(dflt=-1)
        stat_ctxt = tables.Int64Col(dflt=-1)
        stat_processes = tables.Int64Col(dflt=-1)
        stat_procs_blocked = tables.Int64Col(dflt=-1)

        loadavg_1min = tables.Float32Col(dflt=-1)
        loadavg_5min = tables.Float32Col(dflt=-1)
        loadavg_15min = tables.Float32Col(dflt=-1)
        loadavg_runnable = tables.Float32Col(dflt=-1)
        loadavg_total_threads = tables.Float32Col(dflt=-1)

        # sys_numa_zoneallocs = tables.Int64Col(dflt=-1)
        # sys_numa_zoneallocs = tables.Int64Col(dflt=-1)
        # sys_numa_foreign_allocs = tables.Int64Col(dflt=-1)
        # sys_numa_allocation = tables.Int64Col(dflt=-1)
        # sys_numa_allocation = tables.Int64Col(dflt=-1)
        # sys_numa_interleave = tables.Int64Col(dflt=-1)
        
    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)

class HDF5PerfhwCounters(object):
    Counters = get_counters_class("perfhwstats_default")

    class HDF5TableDescription(tables.IsDescription):
        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)

        counter_1 = tables.Int64Col(dflt=-1)
        counter_2 = tables.Int64Col(dflt=-1)
        counter_3 = tables.Int64Col(dflt=-1)
        counter_4 = tables.Int64Col(dflt=-1)
        counter_5 = tables.Int64Col(dflt=-1)

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class HDF5RAPLStatsCounters(object):
    Counters = get_counters_class("RAPLstats_default")

    class HDF5TableDescription(tables.IsDescription):

        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)
        involved_jobs = tables.StringCol(8192)

        counter_1 = tables.Int64Col(dflt=-1)
        counter_2 = tables.Int64Col(dflt=-1)
        counter_3 = tables.Int64Col(dflt=-1)
        counter_4 = tables.Int64Col(dflt=-1)
        counter_5 = tables.Int64Col(dflt=-1)
        counter_6 = tables.Int64Col(dflt=-1)
        counter_7 = tables.Int64Col(dflt=-1)
        counter_8 = tables.Int64Col(dflt=-1)
        counter_9 = tables.Int64Col(dflt=-1)
        counter_10 = tables.Int64Col(dflt=-1)
        counter_11 = tables.Int64Col(dflt=-1)
        counter_12 = tables.Int64Col(dflt=-1)
        counter_13 = tables.Int64Col(dflt=-1)
        counter_14 = tables.Int64Col(dflt=-1)
        counter_15 = tables.Int64Col(dflt=-1)
        counter_16 = tables.Int64Col(dflt=-1)
        counter_17 = tables.Int64Col(dflt=-1)
        counter_18 = tables.Int64Col(dflt=-1)
        counter_19 = tables.Int64Col(dflt=-1)
        counter_20 = tables.Int64Col(dflt=-1)
        counter_21 = tables.Int64Col(dflt=-1)
        counter_22 = tables.Int64Col(dflt=-1)
        counter_23 = tables.Int64Col(dflt=-1)

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class HDF5InfinibandStatsCounters(object):
    Counters = get_counters_class("infinibandstats_default")

    class HDF5TableDescription(tables.IsDescription):

        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)
        involved_jobs = tables.StringCol(8192)
        
        portXmitData = tables.Int64Col(dflt=-1)
        portRcvData = tables.Int64Col(dflt=-1)
        portXmitPkts = tables.Int64Col(dflt=-1)
        portRcvPkts = tables.Int64Col(dflt=-1)

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class HDF5TemperatureStatsCounters(object):
    Counters = get_counters_class("temperaturestats_default")

    class HDF5TableDescription(tables.IsDescription):
        counter_1 = tables.Int64Col(dflt=-1)
        counter_2 = tables.Int64Col(dflt=-1)
        counter_3 = tables.Int64Col(dflt=-1)
        counter_4 = tables.Int64Col(dflt=-1)
        counter_5 = tables.Int64Col(dflt=-1)
        counter_6 = tables.Int64Col(dflt=-1)

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class HDF5LustreStatsCounters(object):
    Counters = get_counters_class("lustrestats_default")

    class HDF5TableDescription(tables.IsDescription):

        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)
        involved_jobs = tables.StringCol(8192)
        
        lustre_nb_read = tables.Int64Col(dflt=-1)
        lustre_bytes_read = tables.Int64Col(dflt=-1)
        lustre_nb_write = tables.Int64Col(dflt=-1)
        lustre_bytes_write = tables.Int64Col(dflt=-1)
        
    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class JobprocstatsCounters(object):
    Counters = get_counters_class("jobprocstats_default")

    class HDF5TableDescription(tables.IsDescription):
        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)
        involved_jobs = tables.StringCol(8192)

        rchar = tables.Int64Col(dflt=-1)
        wchar = tables.Int64Col(dflt=-1)
        syscr = tables.Int64Col(dflt=-1)
        syscw = tables.Int64Col(dflt=-1)
        read_bytes = tables.Int64Col(dflt=-1)
        write_bytes = tables.Int64Col(dflt=-1)
        cancelled_write_bytes = tables.Int64Col(dflt=-1)

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


class IpmipowerstatsCounters(object):
    Counters = get_counters_class("ipmipowerstats_default")

    class HDF5TableDescription(tables.IsDescription):

        timestamp = tables.Int64Col(dflt=-1)
        hostname = tables.StringCol(255)
        job_id = tables.Int64Col(dflt=-1)
        metric_backend = tables.StringCol(255)
        involved_jobs = tables.StringCol(8192)

        average_power_consumption = tables.Int64Col(dflt=-1)        

    missing_keys = []

    @classmethod
    def get_table_description(cls):
        return cls.HDF5TableDescription

    @classmethod
    def to_counters(cls, row):
        counters = cls.Counters()
        for key in list(cls.Counters._header_definitions):
            counters._set_header(key, row[key])

        for key in list(cls.Counters._counter_definitions):
            counters._set_counter(key, row[key])
        return counters

    @classmethod
    def to_row(cls, row, counters):
        for key in list(cls.Counters._header_definitions):
            try:
                row[key] = counters._get_header(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)
        for key in list(cls.Counters._counter_definitions):
            try:
                row[key] = counters._get_counter(key)
            except Exception as e:
                if key not in cls.missing_keys:
                    cls.missing_keys.append(key)
                    LOG.warning(e)


                    
class HDF5OutputBackend(OutputBaseBackend):
    '''
    stdout backend class
    '''
    __backend_name__ = "hdf5"

    def open(self):
        self.stat_buffer = dict()
        self.jobs = {}

    def _get_job_stat(self, job_id):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobFile(self.options, job_id)
        return self.jobs[job_id]

    def close(self):
        for job_file in self.jobs.values():
            job_file.close_job_file()

    def push(self, counters_list):
        '''
        put the metrics to the output backend
        '''
        counters_dict = dict()
        c=0
        for counters in counters_list:
            job_id = counters._get_header('job_id')
            if job_id not in counters_dict:
                counters_dict[job_id] = list()
            counters_dict[job_id].append(counters)

        for (job_id, c_list) in counters_dict.items():
            jobstat = self._get_job_stat(job_id)
            jobstat.append_stats(c_list)
            c+=len(c_list)
        LOG.info("HDF5: Pushed %s metrics" % c) 

class FileAccess(object):
    '''
    Share the access to one or several between each monitored job
    '''
    def __init__(self):
        self.hdf5_files = dict()

    def _open_hdf5_file(self, path, filemode, filters):
        """
        Open the hdf5 file corresponding to the job.
        """
        LOG.debug("Opening the file %s" % path)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        hdf5_file = tables.open_file(path, filemode, filters=filters)

        return hdf5_file

    def open_file(self, path, filemode, filters=None):
        if path in self.hdf5_files:
            hdf5_file = self.hdf5_files[path]
            if hdf5_file.isopen:
                return hdf5_file
        hdf5_file = self._open_hdf5_file(path, filemode, filters=filters)
        self.hdf5_files[path] = hdf5_file
        return hdf5_file

    def close_file_by_path(self, path):
        if path in self.hdf5_files:
            self.hdf5_files[path].close()


class JobFile(object):
    fileaccess = FileAccess()
    hdf5_counters = {
        'taskstats_default': HDF5TaskstatsCounters,
        'procstats_default': HDF5ProcstatsCounters,
        'infinibandstats_default': HDF5InfinibandStatsCounters,
        'temperaturestats_default': HDF5TemperatureStatsCounters,
        'lustrestats_default': HDF5LustreStatsCounters,
        'RAPLstats_default': HDF5RAPLStatsCounters,
        'perfhwstats_default': HDF5PerfhwCounters,
        'jobprocstats_default': JobprocstatsCounters,
        'ipmipowerstats_default': IpmipowerstatsCounters
    }
    path_level = 4

    def __init__(self, options, job_id, filemode="a"):
        self.options = options
        self.job_id = job_id
        self.job_file = None
        self.job_filemode = filemode
        self.job_table = {} # one table per metric's backend

        self.job_backend_version = None
        
        if hasattr(options, 'hdf5_filepath') \
                and options.hdf5_filepath is not None:
            self.hdf5_filepath = options.hdf5_filepath
        else:
            self.hdf5_filepath = "/tmp/colmet/hdf5/counters"

        if hasattr(options, 'hdf5_complevel'):
            self.hdf5_complevel = options.hdf5_complevel
        else:
            self.hdf5_complevel = 0
        if hasattr(options, 'hdf5_complib'):
            self.hdf5_complib = options.hdf5_complib
        else:
            self.hdf5_complib = None

        LOG.debug("Writing counters in hdf5 format for job %s"
                  % self.job_id)

    def _open_job_file(self):
        """
        Open the hdf5 file corresponding to the job.
        """
        if self.hdf5_complevel == 0 or self.hdf5_complib is None:
            self.job_file = JobFile.fileaccess.open_file(self.hdf5_filepath,
                                                         self.job_filemode)
        else:
            LOG.debug("HDF5 compression enabled (lib=%s, level=%s) for %s" %
                     (self.hdf5_complib, self.hdf5_complevel,
                      self.hdf5_filepath))
            filters = tables.Filters(complevel=self.hdf5_complevel,
                                     complib=self.hdf5_complib)
            self.job_file = JobFile.fileaccess.open_file(self.hdf5_filepath,
                                                         self.job_filemode,
                                                         filters=filters)

    def close_job_file(self):
        """
        Close the hdf5 file corresponding to the job.
        """
        JobFile.fileaccess.close_file_by_path(self.hdf5_filepath)


    def _init_job_file_if_needed(self):
        self._open_job_file()

        group_name = "job_%s" % self.job_id
        group_path = "/%s" % group_name
        if group_path not in self.job_file:
            root = self.job_file.root
            self.job_file.create_group(root, group_name)


    def _init_job_table_if_needed(self, metric_backend):

        group_name = "job_%s" % self.job_id
        group_path = "/%s" % group_name

        table_name = metric_backend
        table_path = "%s/%s" % (group_path, table_name)
        
        if table_path not in self.job_file:
            if metric_backend is None:
                raise ValueError(
                    "The metric backend must be "
                    "defined to create the table"
                )

            job_metric_hdf5_class = self.hdf5_counters[metric_backend]
            self.job_file.create_table(
                group_path,
                table_name,
                job_metric_hdf5_class.get_table_description(),
                "Metrics for the Job %s" % self.job_id
            )
            self.job_table[metric_backend] = self.job_file.get_node(table_path)
            self.job_table[metric_backend].set_attr('backend_version', HDF5_BACKEND_VERSION)

        else:
            self.job_table[metric_backend] = self.job_file.get_node(table_path)
            self.job_backend_version = self.job_table[metric_backend].get_attr('backend_version')
            

    def append_stats(self, stats):
        for stat in stats:
            metric_backend = stat.metric_backend
            if self.job_file is None:
                self._init_job_file_if_needed()

            if metric_backend not in self.job_table:
                self._init_job_table_if_needed(metric_backend)

            row = self.job_table[metric_backend].row
            job_metric_hdf5_class = self.hdf5_counters[metric_backend]
            job_metric_hdf5_class.to_row(row, stat)
            row.append()
            self.job_table[metric_backend].flush()
