import os
import re

from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job
from colmet.common.metrics.procstats import ProcstatsCounters



class ProcstatsBackend(InputBaseBackend):
    __backend_name__ = "procstats"

    def open(self):
        self.procstats = ProcStats(self.options)
        # job with id equal to 0 is the fictive job to gather nodes' monitoring measures
        self.job_0 = Job(self, 0, self.options)

    def close(self):
        pass

    def get_procstats(self):
        counters = self.procstats.get_stats()
        return counters

    def get_counters_class(self):
        return ProcstatsCounters

    def pull(self):
        self.job_0.update_stats()
        return self.job_0.get_stats()

#
# The source part below is largely inspired by procstats.py file from open TSDB projet
#
# This file is part of tcollector.
# Copyright (C) 2010  StumbleUpon, Inc.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.

NUMADIR = "/sys/devices/system/node"

class ProcStats(object):

    def __init__(self,option):
        self.options = option

        self.f_uptime = open("/proc/uptime", "r")
        self.f_meminfo = open("/proc/meminfo", "r")
        self.f_vmstat = open("/proc/vmstat", "r")
        self.f_stat = open("/proc/stat", "r")
        self.f_loadavg = open("/proc/loadavg", "r")
        self.f_entropy_avail = open("/proc/sys/kernel/random/entropy_avail", "r")
#       self.numastats = self.open_sysfs_numa_stats()

# NOT USED TODO
    def open_sysfs_numa_stats():
        """Returns a possibly empty list of opened files."""
        try:
            nodes = os.listdir(NUMADIR)
        except OSError, (errno, msg):
            if errno == 2:  # No such file or directory
                return []   # We don't have NUMA stats.
            raise

        nodes = [node for node in nodes if node.startswith("node")]
        numastats = []
        for node in nodes:
            try:
                numastats.append(open(os.path.join(NUMADIR, node, "numastat")))
            except OSError, (errno, msg):
                if errno == 2:  # No such file or directory
                    continue
                raise
        return numastats


    def get_stats(self):
        # proc.uptime
        procstats_data = {}
        self.f_uptime.seek(0)
        for line in self.f_uptime:
            m = re.match("(\S+)\s+(\S+)", line)
            if m:
                uptime_total = int(float(m.group(1)))
                uptime_idle = int(float(m.group(2)))

        procstats_data['uptime_total'] = uptime_total
        procstats_data['uptime_idle'] = uptime_idle

        # proc.meminfo
        self.f_meminfo.seek(0)
        for line in self.f_meminfo:
            m = re.match("(\w+):\s+(\d+)", line)
            if m:
                #print ("proc.meminfo.%s  %s" % (m.group(1).lower(), ts, m.group(2)))
                #print "meminfo_" + m.group(1).lower()
                procstats_data["meminfo_" + m.group(1).lower()] = int(m.group(2))

        # proc.vmstat
        self.f_vmstat.seek(0)
        for line in self.f_vmstat:
            m = re.match("(\w+)\s+(\d+)", line)
            if not m:
                continue
            if m.group(1) in ("pgpgin", "pgpgout", "pswpin", "pswpout", "pgfault", "pgmajfault"):
                #print "proc.vmstat.%s %s" % (m.group(1), m.group(2))
                procstats_data["vmstat_" + m.group(1)] = int(m.group(2))

        # proc.stat
        self.f_stat.seek(0)
        for line in self.f_stat:
            m = re.match("(\w+)\s+(.*)", line)
            if not m:
               continue
            if m.group(1) == "cpu":
                fields = m.group(2).split()
                procstats_data['stat_cpu_user'] = int(fields[0])
                procstats_data['stat_cpu_nice'] = int(fields[1])
                procstats_data['stat_cpu_system'] = int(fields[2])
                procstats_data['stat_cpu_idle'] = int(fields[3])
                procstats_data['stat_cpu_iowait'] = int(fields[4])
                procstats_data['stat_cpu_irq'] = int(fields[5])
                procstats_data['stat_cpu_softirq'] = int(fields[6])
                procstats_data['stat_cpu_guest'] = int(fields[7])
                procstats_data['stat_cpu_guest_nice'] = int(fields[8])

#               print "proc.stat.cpu %d %s type=user" % (ts, fields[0])
#               print "proc.stat.cpu %d %s type=nice" % (ts, fields[1])
#               print "proc.stat.cpu %d %s type=system" % (ts, fields[2])
#               print "proc.stat.cpu %d %s type=idle" % (ts, fields[3])
#               print "proc.stat.cpu %d %s type=iowait" % (ts, fields[4])
#               print "proc.stat.cpu %d %s type=irq" % (ts, fields[5])
#               print "proc.stat.cpu %d %s type=softirq" % (ts, fields[6])
               # really old kernels don't have this field
#               if len(fields) > 7:
#                    print ("proc.stat.cpu %d %s type=guest"
#                           % (ts, fields[7]))
#                    # old kernels don't have this field
#                    if len(fields) > 8:
#                        print ("proc.stat.cpu %d %s type=guest_nice"
#                               % (ts, fields[8]))

            elif m.group(1) == "intr":
#               print ("proc.stat.intr %d %s"  % (ts, m.group(2).split()[0]))
                procstats_data['stat_intr'] =  int(m.group(2).split()[0])
            elif m.group(1) == "ctxt":
#                print "proc.stat.ctxt %d %s" % (ts, m.group(2))
                procstats_data['stat_ctxt'] = int(m.group(2))
            elif m.group(1) == "processes":
#                print "proc.stat.processes %d %s" % (ts, m.group(2))
                procstats_data['stat_processes'] = int(m.group(2))
            elif m.group(1) == "procs_blocked":
#                print "proc.stat.procs_blocked %d %s" % (ts, m.group(2))
                procstats_data['stat_procs_blocked'] = int(m.group(2))

        self.f_loadavg.seek(0)
        for line in self.f_loadavg:
            m = re.match("(\S+)\s+(\S+)\s+(\S+)\s+(\d+)/(\d+)\s+", line)
            if not m:
                continue

            procstats_data['loadavg_1min'] =  float(m.group(1))
            procstats_data['loadavg_5min'] =  float(m.group(2))
            procstats_data['loadavg_15min'] = float(m.group(3))
            procstats_data['loadavg_runnable'] = float(m.group(4))
            procstats_data['loadavg_total_threads'] = float(m.group(5))

#        f_entropy_avail.seek(0)
#        ts = int(time.time())
#        for line in f_entropy_avail:
#            print "proc.kernel.entropy_avail %d %s" % (ts, line.strip())
#
#        print_numa_stats(numastats)
#
#

        return ProcstatsCounters(procstats_buffer = procstats_data)
