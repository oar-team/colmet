"""This package contains class for representing colmet data"""
import time
import os
import socket
import logging

LOG = logging.getLogger()

from .exceptions import NoJobFoundError


class Info(object):
    '''
    Base class for Information class that do the common initialization
    '''
    def __init__(self, input_backend):
        self.input_backend = input_backend
        self.counters_class = input_backend.get_counters_class()
        self.stats_total = self.counters_class()
        self.stats_delta = None

    def get_stats(self):
        return self.stats_total

    def update_stats(self, timestamp, job_id, hostname):
        self.stats_total.timestamp = timestamp
        self.stats_total.job_id = job_id
        self.stats_total.hostname = hostname


class TaskInfo(Info):
    '''
    Represent Information corresponding to a task
    '''
    def __init__(self, tid, input_backend):
        Info.__init__(self, input_backend)
        self.tid = tid
        self.mark = True
        self.backend_request = self.counters_class.build_request(input_backend, tid)

    def update_stats(self, timestamp, job_id, hostname):
        '''
        Update the current metrics of the task
        '''
        stats = self.counters_class.fetch(self.input_backend, self.backend_request)
        if stats:
            if not self.stats_delta:
                self.stats_total = stats
                self.stats_delta = stats
            stats.delta(self.stats_total, self.stats_delta)
            self.stats_total = stats
            self.mark = False
        Info.update_stats(self, timestamp, job_id, hostname)


class ProcessInfo(Info):
    '''
    Representing the information corresponding to a process
    '''
    def __init__(self, pid, input_backend):
        Info.__init__(self, input_backend)
        self.tgid = pid
        self.tasks = {}
        self.get_task(pid)
        self.mark = True

    def update_stats(self, timestamp, job_id, hostname):
        '''
        Update the current metrics of the process
        '''
        for tid in self.list_tids():
            task = self.get_task(tid)
            task.update_stats(timestamp, job_id, hostname)

        stats_delta = self.counters_class()
        stats_delta.type = 'process'
        stats_delta.id = self.tgid

        for tid, task in self.tasks.items():
            if task.mark:
                msg = (
                    "Task %s no more exists."
                    "Removing from the Job %s"
                    % (tid, self.tgid)
                )
                LOG.debug(msg)
                del self.tasks[tid]
            else:
                task.mark = True
                stats_delta.accumulate(task.stats_delta, stats_delta)

        self.stats_delta = stats_delta
        if not self.stats_total:
            self.stats_total = stats_delta
        else:
            self.stats_total.accumulate(stats_delta, self.stats_total)

        self.mark = False
        Info.update_stats(self, timestamp, job_id, hostname)

        return True

    def get_process(self, tgid):
        '''
        Retrieve the process corresponding to the tgid
        '''
        if tgid != self.tgid:
            return None
        return self

    def list_tids(self):
        '''
        Retrieve the list of tasks of the current process
        '''
        try:
            tids = map(int, os.listdir('/proc/%d/task' % self.tgid))
        except OSError:
            self.mark = True
            return []

        return tids

    def get_task(self, tid):
        '''
        Retrieve the task corresponding to the task id 'tid'
        '''
        task = self.tasks.get(tid, None)
        if not task:
            task = TaskInfo(tid, self.input_backend)
            self.tasks[tid] = task
        return task


class CGroupInfo(Info):
    '''
    Represent the information corresponding to a cgroup
    '''
    def __init__(self, cgroup_path, input_backend):
        Info.__init__(self, input_backend)
        self.cgroup_path = cgroup_path
        self.tasks = {}

    def list_tids(self):
        '''
        Return the list of tasks of the current process
        '''
        try:
            f_tasks = open(os.path.join(self.cgroup_path, 'tasks'), 'r')
            pids = map(int, f_tasks.read().split())
            f_tasks.close()
        except OSError:
            return []
        except IOError:
            return []
        return pids

    def get_task(self, tid):
        '''
        Return the task corresponding to the given tid
        '''
        task = self.tasks.get(tid, None)
        if not task:
            task = TaskInfo(tid, self.input_backend)
            self.tasks[tid] = task
        return task

    def update_stats(self, timestamp, job_id, hostname):
        '''
        Update the current metrics for this cgroup.
        '''

        stats_delta = self.counters_class()
        stats_delta.type = 'cgroup'
        stats_delta.id = self.cgroup_path

        if len(self.list_tids()) > 0:
            for tid in self.list_tids():
                task = self.get_task(tid)
                task.update_stats(timestamp, job_id, hostname)

            for tid, task in self.tasks.items():
                if  task.mark:
                    msg = (
                        "Process/Task %s no more exists."
                        "Removing from the Job %s"
                        % (tid, self.cgroup_path)
                    )
                    LOG.debug(msg)
                    del self.tasks[tid]
                else:
                    task.mark = True
                    stats_delta.accumulate(task.stats_delta, stats_delta)

            self.stats_delta = stats_delta
            self.stats_total.accumulate(stats_delta, self.stats_total)

            self.void_cpuset = False

        else:  # no task in this cgroup....
            LOG.info("no taks in this cgroup")
            #raise VoidCpusetError

        Info.update_stats(self, timestamp, job_id, hostname)
        return True


class ProcStatsInfo(Info):
    '''
    Represent the information corresponding to a node (not only one job)
    '''
    def __init__(self, input_backend):
        Info.__init__(self, input_backend)
        self.input_backend = self.input_backend

    def update_stats(self, timestamp, job_id, hostname):
        '''
        Update the current metrics for the node (job_id=0)
        '''
        stats = self.counters_class.fetch(self.input_backend)
        if stats:
            if not self.stats_delta:
                self.stats_total = stats
                self.stats_delta = stats
            stats.delta(self.stats_total, self.stats_delta)
            self.stats_total = stats

        Info.update_stats(self, timestamp, job_id, hostname)

        return True


class Job(object):
    '''
    Represent the Job to monitor
    '''
    def __init__(self, input_backend, job_id, options):
        self.job_children = []
        self.input_backend = input_backend
        self.options = options
        self.timestamp = int(time.time())
        self.duration = None
        self.job_id = job_id
        self._hostname = socket.gethostname()
        #void_cpuset is used to avoid sending null stats to output backends TODO rm
        self.void_cpuset = True

        self.job_children.extend(
            [TaskInfo(tid, input_backend) for tid in options.tids]
        )
        self.job_children.extend(
            [ProcessInfo(pid, input_backend) for pid in options.pids]
        )
        self.job_children.extend(
            [CGroupInfo(cgroup, input_backend) for cgroup in options.cgroups]
        )

        #to monitor global node resources activities
        if job_id == 0:
            self.job_children.extend([ProcStatsInfo(input_backend)])

        number_of_child = len(self.job_children)
        if number_of_child == 0:
            raise NoJobFoundError
        msg = "the job contains %s items" % (number_of_child)
        LOG.info(msg)

        self.update_stats()

    def list_tgids(self):
        '''
        Return the list of process id corresponding to the running jobs
        '''

        tgids = []
        for item in self.job_children:
            tgids.extend(item.list_tgids())

        current_tgids = Job.list_running_tgids()

        return list(set(current_tgids).intersection(set(tgids)))

    @staticmethod
    def list_running_tgids():
        '''
        Return the list of process id currently running
        '''
        proc_ls = os.listdir('/proc')
        return [int(tgid) for tgid in proc_ls if '0' <= tgid[0] <= '9']

    def update_stats(self):
        '''
        Update the metrics for all the job's children
        '''
        new_timestamp = int(time.time())
        self.duration = new_timestamp - self.timestamp
        self.timestamp = new_timestamp

        for item in self.job_children:
            item.update_stats(self.timestamp, self.job_id, self._hostname)

    def get_children(self):
        '''
        Return the job lists
        '''
        return self.job_children

    def get_stats(self):
        return [child.get_stats() for child in self.job_children]
