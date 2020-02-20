import os
import re
import errno
import struct
import copy
import logging

from colmet.common.metrics.taskstats import TaskstatsCounters
from colmet.common.exceptions import (NoEnoughPrivilegeError,
                                      JobNeedToBeDefinedError)
from colmet.common.backends.base import InputBaseBackend
from colmet.common.job import Job

LOG = logging.getLogger()


class TaskstatsBackend(InputBaseBackend):

    __backend_name__ = "taskstats"

    def open(self):
        self.jobs = {}

        self.taskstats_nl = TaskStatsNetlink(self.options)

        if len(self.job_id_list) < 1 \
                and self.options.cpuset_rootpath == []:
            raise JobNeedToBeDefinedError()
        if len(self.job_id_list) == 1:
            job_id = self.job_id_list[0]
            self.jobs[job_id] = Job(self, job_id, self.options)
        else:
            for i, job_id in enumerate(self.job_id_list):
                self.jobs[job_id] = Job(self, job_id, self.options)

    def close(self):
        pass

    def build_request(self, pid):
        return self.taskstats_nl.build_request(pid)

    def get_task_stats(self, request):
        counters = self.taskstats_nl.get_single_task_stats(request)
        return counters

    def pull(self):
        values=list(self.jobs.values())
        for job in values:
            LOG.debug("pull job :" + str(job.job_id))
            job.update_stats()
        return [job.get_stats() for job in values]

    def get_counters_class(self):
        return TaskstatsCounters

    def create_options_job_cgroups(self, cgroups):
        # options are duplicated to allow modification per jobs, here
        # cgroups parametter
        options = copy.copy(self.options)
        options.cgroups = cgroups
        return options

    def update_job_list(self):
        """Used to maintained job list upto date by adding new jobs and
        removing ones to monitor accordingly to cpuset_rootpath and
        regex_job_id.
        """
        cpuset_rootpath = self.options.cpuset_rootpath[0]
        regex_job_id = self.options.regex_job_id[0]

        job_ids = set([])
        filenames = {}
        for filename in os.listdir(cpuset_rootpath):
            jid = re.findall(regex_job_id, filename)
            if len(jid) > 0:
                job_ids.add(jid[0])
                filenames[jid[0]] = filename

        monitored_job_ids = set(self.job_id_list)
        # Add new jobs
        for job_id in (job_ids - monitored_job_ids):
            job_path = cpuset_rootpath + "/" + filenames[job_id]
            options = self.create_options_job_cgroups([job_path])
            self.jobs[job_id] = Job(self, int(job_id), options)
        # Del ended jobs

        for job_id in (monitored_job_ids - job_ids):
            del self.jobs[job_id]
        # udpate job_id list to monitor
        self.job_id_list = list(job_ids)

#
# Taskstats Netlink
#

from .genetlink.netlink import Connection, NETLINK_GENERIC, U32Attr, \
    NLM_F_REQUEST
from .genetlink.genetlink import Controller, GeNlMessage

TASKSTATS_CMD_GET = 1

TASKSTATS_CMD_ATTR_PID = 1
TASKSTATS_CMD_ATTR_TGID = 2

TASKSTATS_TYPE_PID = 1
TASKSTATS_TYPE_TGID = 2
TASKSTATS_TYPE_STATS = 3
TASKSTATS_TYPE_AGGR_PID = 4
TASKSTATS_TYPE_AGGR_TGID = 5


class TaskStatsNetlink(object):
    # Keep in sync with format_stats() and pinfo.did_some_io()

    def __init__(self, options):
        self.options = options
        self.connection = Connection(NETLINK_GENERIC)
        controller = Controller(self.connection)
        self.family_id = controller.get_family_id('TASKSTATS')

    def build_request(self, tid):
        return GeNlMessage(self.family_id, cmd=TASKSTATS_CMD_GET,
                           attrs=[U32Attr(TASKSTATS_CMD_ATTR_PID, tid)],
                           flags=NLM_F_REQUEST)

    def get_single_task_stats(self, request):
        request.send(self.connection)
        try:
            reply = GeNlMessage.recv(self.connection)
        except OSError as e:
            if e.errno == errno.ESRCH:
                # OSError: Netlink error: No such process (3)
                return
            if e.errno == errno.EPERM:
                raise NoEnoughPrivilegeError
            raise
        for attr_type, attr_value in reply.attrs.items():
            if attr_type == TASKSTATS_TYPE_AGGR_PID:
                reply = attr_value.nested()
                break
            # elif attr_type == TASKSTATS_TYPE_PID:
            #    pass
        else:
            return
        taskstats_data = reply[TASKSTATS_TYPE_STATS].data
        if len(taskstats_data) < 272:
            # Short reply
            return
        taskstats_version = struct.unpack('H', taskstats_data[:2])[0]
        assert taskstats_version >= 4
        return TaskstatsCounters(taskstats_buffer=taskstats_data)
