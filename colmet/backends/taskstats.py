
import errno
import struct

from colmet.metrics.taskstats_default import get_taskstats_class
from colmet.exceptions import NoEnoughPrivilegeError, JobNeedToBeDefinedError, OnlyOneJobIsSupportedError
from colmet.backends.base import InputBaseBackend
from colmet.job import Job

Counters = get_taskstats_class()

def get_input_backend_class():
    return TaskStatsNodeBackend

class TaskStatsNodeBackend(InputBaseBackend):
    def __init__(self, options):
        InputBaseBackend.__init__(self,options)
        self.options = options
        self.taskstats_nl = TaskStatsNetlink(options)

        if len(self.job_id_list) < 1:
            raise JobNeedToBeDefinedError()
        if len(self.job_id_list) > 1:
            raise OnlyOneJobIsSupportedError()

        self.job = Job(self,self.job_id_list[0],options)
    
    @classmethod
    def _get_backend_name(cls):
        return "taskstats"

    def build_request(self, pid):
        return self.taskstats_nl.build_request(pid)
    
    def get_task_stats(self, request):
        counters = self.taskstats_nl.get_single_task_stats(request)
        return counters

    def pull(self):
        self.job.update_stats()
        return self.job.get_stats()

    def get_counters_class(self):
        return Counters



#
# Taskstats Netlink
# 

from genetlink.netlink import Connection, NETLINK_GENERIC, U32Attr, NLM_F_REQUEST
from genetlink.genetlink import Controller, GeNlMessage

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
        except OSError, e:
            if e.errno == errno.ESRCH:
                # OSError: Netlink error: No such process (3)
                return
            if e.errno == errno.EPERM:
                raise NoEnoughPrivilegeError
            raise
        for attr_type, attr_value in reply.attrs.iteritems():
            if attr_type == TASKSTATS_TYPE_AGGR_PID:
                reply = attr_value.nested()
                break
            #elif attr_type == TASKSTATS_TYPE_PID:
            #    pass
        else:
            return
        taskstats_data = reply[TASKSTATS_TYPE_STATS].data
        if len(taskstats_data) < 272:
            # Short reply
            return
        taskstats_version = struct.unpack('H', taskstats_data[:2])[0]
        assert taskstats_version >= 4
        return Counters(taskstats_buffer = taskstats_data)


