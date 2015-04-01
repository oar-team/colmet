
import struct
import logging


LOG = logging.getLogger()

from .base import UInt8, UInt16, UInt32, UInt64, String, BaseCounters


class TaskstatsCounters(BaseCounters):
    __metric_name__ = 'taskstats_default'

    counters_taskstats = {
        # 'key' : ( offset,length, type, repr, acc, init_value )
        #
        # /* The version number of this struct. This field is always set to
        #  * TAKSTATS_VERSION, which is defined in <linux/taskstats.h>.
        #  * Each time the struct is changed, the value should be incremented.
        #  */
        # __u16   version;
        'version': (0, UInt16(), '', 'none', 'Version'),
        # __u32   ac_exitcode;            /* Exit status */
        'ac_exitcode': (2, UInt32(), '', 'none', 'Exit code'),

        # /* The accounting flags of a task as defined in <linux/acct.h>
        #  * Defined values are AFORK, ASU, ACOMPAT, ACORE, and AXSIG.
        #  */
        # __u8    ac_flag;                /* Record flags */
        'ac_flag': (6, UInt8(), '', 'none', 'Flag'),
        # __u8    ac_nice;                /* task_nice */
        'ac_nice': (7, UInt8(), '', 'none', 'Nice'),

        # /* Delay accounting fields start
        #  *
        #  * All values, until comment "Delay accounting fields end" are
        #  * available only if delay accounting is enabled, even though the
        #  * last few fields are not delays
        #  *
        #  * xxx_count is the number of delay values recorded
        #  * xxx_delay_total is the corresponding cumulative delay in
        #  * nanoseconds
        #  *
        #  * xxx_delay_total wraps around to zero on overflow
        #  * xxx_count incremented regardless of overflow
        #  */

        # /* Delay waiting for cpu, while runnable
        #  * count, delay_total NOT updated atomically
        #  */
        # __u64   cpu_count __attribute__((aligned(8)));
        'cpu_count': (16, UInt64(), 'count', 'add',
                      "Nb of cpu delay values recorded"),
        # __u64   cpu_delay_total;
        'cpu_delay_total': (24, UInt64(), 'nsec', 'add',
                            "Total of cumulative cpu delay"),

        # /* Following four fields atomically updated using task->delays->lock
        #  */

        # /* Delay waiting for synchronous block I/O to complete
        #  * does not account for delays in I/O submission
        #  */
        # __u64   blkio_count;
        'blkio_count': (32, UInt64(), 'count', 'add',
                        "Nb of block I/O delay values recorded"),
        # __u64   blkio_delay_total;
        'blkio_delay_total': (40, UInt64(), 'nsec', 'add',
                              "Total of cumulative block I/O delay"),

        # /* Delay waiting for page fault I/O (swap in only) */
        # __u64   swapin_count;
        'swapin_count': (48, UInt64(), 'count', 'add',
                         "Nb of swapin delay calues recorded"),
        # __u64   swapin_delay_total;
        'swapin_delay_total': (56, UInt64(), 'nsec', 'add',
                               "Total of cumulative swapin delay"),

        # /* cpu "wall-clock" running time
        #  * On some architectures, value will adjust for cpu time stolen
        #  * from the kernel in involuntary waits due to virtualization.
        #  * Value is cumulative, in nanoseconds, without a corresponding count
        #  * and wraps around to zero silently on overflow
        #  */
        # __u64   cpu_run_real_total;
        'cpu_run_real_total': (64, UInt64(), 'nsec', 'add',
                               "Total of cumulative cpu run real"),

        # /* cpu "virtual" running time
        #  * Uses time intervals seen by the kernel i.e. no adjustment
        #  * for kernel's involuntary waits due to virtualization.
        #  * Value is cumulative, in nanoseconds, without a corresponding count
        #  * and wraps around to zero silently on overflow
        #  */
        # __u64   cpu_run_virtual_total;
        'cpu_run_virtual_total': (72, UInt64(), 'nsec', 'add',
                                  "Total of cumulative cpu run virtual"),
        # /* Delay accounting fields end */
        # /* version 1 ends here */

        # /* Basic Accounting Fields start */
        # char    ac_comm[TS_COMM_LEN];   /* Command name */
        'ac_comm': (80, String(32), 'string', 'none', ""),
        # __u8    ac_sched __attribute__(aligned(8: 'none'));
        # /* Scheduling discipline */
        'ac_shed': (112, UInt8(), '', 'none', ""),
        # __u8    ac_pad[3];
        'ac_pad': (113, String(3), '', 'none', ""),
        # __u32   ac_uid __attribute__(aligned(8: 'none'));
        'ac_uid': (120, UInt32(), '', 'none', ""),
        # /* User ID */
        # __u32   ac_gid;                 /* Group ID */
        'ac_gid': (124, UInt32(), '', 'none', ""),
        # __u32   ac_pid;                 /* Process ID */
        'ac_pid': (128, UInt32(), '', 'none', ""),
        # __u32   ac_ppid;                /* Parent process ID */
        'ac_ppid': (132, UInt32(), '', 'none', ""),
        # __u32   ac_btime;               /* Begin time [sec since 1970] */
        'ac_btime': (136, UInt32(), 'ts_date', 'min', "Begin time"),
        # __u64   ac_etime __attribute__   (aligned(8: 'add'));
        # /* Elapsed time [usec] */
        'ac_etime': (144, UInt64(), 'usec', 'max', "Elasped time"),
        # __u64   ac_utime;               /* User CPU time [usec] */
        'ac_utime': (152, UInt64(), 'usec', 'add', "User CPU time"),
        # __u64   ac_stime;               /* SYstem CPU time [usec] */
        'ac_stime': (160, UInt64(), 'usec', 'add', "System CPU time"),
        # __u64   ac_minflt;              /* Minor Page Fault Count */
        'ac_minflt': (168, UInt64(), 'count', 'add', "Minor Page Fault Count"),
        # __u64   ac_majflt;              /* Major Page Fault Count */
        'ac_majflt': (176, UInt64(), 'count', 'add', "Major Page Fault Count"),
        # /* Basic Accounting Fields end */

        # /* Extended accounting fields start */
        # /* Accumulated RSS usage in duration of a task, in MBytes-usecs.
        #  * The current rss usage is added to this counter every time
        #  * a tick is charged to a task's system time. So, at the end we
        #  * will have memory usage multiplied by system time. Thus an
        #  * average usage per system time unit can be calculated.
        #  */
        # __u64   coremem;               /* accumulated RSS usage in MB-usec */
        'coremem': (184, UInt64(), 'mbytes-usec', 'add',
                    "Accumulated RSS usage"),
        # /* Accumulated virtual memory usage in duration of a task.
        #  * Same as acct_rss_mem1 above except that we keep track of VM usage.
        #  */
        # __u64   virtmem;               /* accumulated VM  usage in MB-usec */
        'virtmem': (192, UInt64(), 'mbytes-usec', 'add',
                    "Accumulated VM usage"),

        # /* High watermark of RSS and virtual memory usage in duration of
        #  * a task, in KBytes.
        #  */
        # __u64   hiwater_rss;         /* High-watermark of RSS usage, in KB */
        'hiwater_rss': (200, UInt64(), 'kbytes', 'max',
                        "High-watermark of RSS usage"),
        # __u64   hiwater_vm;             /* High-water VM usage, in KB */
        'hiwater_vm': (208, UInt64(), 'kbytes', 'max', "High-water VM usage"),

        # /* The following four fields are I/O statistics of a task. */
        # __u64   read_char;              /* bytes read */
        'read_char': (216, UInt64(), 'bytes', 'add', "Bytes read"),
        # __u64   write_char;             /* bytes written */
        'write_char': (224, UInt64(), 'bytes', 'add', "Bytes written"),
        # __u64   read_syscalls;          /* read syscalls */
        'read_syscalls': (232, UInt64(), 'count', 'add', "Read syscalls"),
        # __u64   write_syscalls;         /* write syscalls */
        'write_syscalls': (240, UInt64(), 'count', 'add', "Write syscalls"),
        # /* Extended accounting fields end */

        # define TASKSTATS_HAS_IO_ACCOUNTING
        # /* Per-task storage I/O accounting starts */
        # __u64   read_bytes;             /* bytes of read I/O */
        'read_bytes': (248, UInt64(), 'bytes', 'add', "Read I/O"),
        # __u64   write_bytes;            /* bytes of write I/O */
        'write_bytes': (256, UInt64(), 'bytes', 'add', "Write I/O"),
        # __u64   cancelled_write_bytes;  /* bytes of cancelled write I/O */
        'cancelled_write_bytes': (264, UInt64(), 'bytes', 'add',
                                  "Cancelled write I/O"),

        # __u64  nvcsw;                   /* voluntary_ctxt_switches */
        'nvcsw': (272, UInt64(), 'count', 'add', "Voluntary context switches"),

        # __u64  nivcsw;                  /* nonvoluntary_ctxt_switches */
        'nivcsw': (280, UInt64(), 'count', 'add',
                   "Non-volontary context switches"),
        # /* time accounting for SMT machines */
        # __u64   ac_utimescaled;         /* utime scaled on frequency etc */
        'ac_utimescaled': (288, UInt64(), 'usec', 'add',
                           "User CPU time scaled on frequency"),
        # __u64   ac_stimescaled;         /* stime scaled on frequency etc */
        'ac_stimescaled': (296, UInt64(), 'usec', 'add',
                           "System CPU time scaled on frequency"),
        # __u64   cpu_scaled_run_real_total; /* scaled cpu_run_real_total */
        'cpu_scaled_run_real_total':
            (304, UInt64(), 'nsec',
             'add', "CPU run real total scaled on frequency"),

        # /* Delay waiting for memory reclaim */
        # __u64   freepages_count;
        'freepages_count': (312, UInt64(), 'count', 'add',
                            "Number of freepages delay values recorded"),
        # __u64   freepages_delay_total;
        'freepages_delay_total': (320, UInt64(), 'nsec', 'add',
                                  "Total of cumulative freepages delay"),
    }

    counters_taskstats_to_get = [
        # 'version',
        # 'ac_exitcode',
        # 'ac_flag',
        # 'ac_nice',
        'cpu_count',
        'cpu_delay_total',
        'blkio_count',
        'blkio_delay_total',
        'swapin_count',
        'swapin_delay_total',
        'cpu_run_real_total',
        'cpu_run_virtual_total',
        # 'ac_comm',
        # 'ac_shed',
        # 'ac_pad',
        # 'ac_uid',
        # 'ac_gid',
        # 'ac_pid',
        # 'ac_ppid',
        'ac_btime',
        'ac_etime',
        'ac_utime',
        'ac_stime',
        'ac_minflt',
        'ac_majflt',
        'coremem',
        'virtmem',
        # 'hiwater_rss',
        # 'hiwater_vm',
        'read_char',
        'write_char',
        'read_syscalls',
        'write_syscalls',
        'read_bytes',
        'write_bytes',
        'cancelled_write_bytes',
        'nvcsw',
        'nivcsw',
        'ac_utimescaled',
        'ac_stimescaled',
        'cpu_scaled_run_real_total',
        'freepages_count',
        'freepages_delay_total',
    ]

    _counters = []
    for c_name in counters_taskstats_to_get:
        (_, c_type, c_repr, c_acc, c_descr) = counters_taskstats[c_name]
        _counters.append((c_name, c_type, c_repr, c_acc, c_descr))

    @classmethod
    def get_zero_counters(cls):
        return cls(taskstats_buffer=None, raw=None)

    @classmethod
    def fetch(cls, taskstat_backend, request):
        return taskstat_backend.get_task_stats(request)

    @classmethod
    def build_request(cls, taskstats_backend, tid):
        return taskstats_backend.build_request(tid)

    def __init__(self, taskstats_buffer=None, raw=None):
        BaseCounters.__init__(self, raw=raw)
        if raw is not None:
            pass
        elif taskstats_buffer is None:
            self._empty_fill()
        else:
            for name in TaskstatsCounters._counter_definitions:
                packed_values = TaskstatsCounters.counters_taskstats[name]
                (c_offset, c_type, _, _, _) = packed_values
                data = taskstats_buffer[c_offset:c_offset + c_type.length]
                unpacked_struct = struct.unpack(c_type.struct_code, data)
                self._counter_values[name] = unpacked_struct[0]
