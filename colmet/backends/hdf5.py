'''
stdout backend : print information to stdout
'''

import os
import logging

LOG = logging.getLogger()

HDF5_BACKEND_VERSION = 2

import tables
import numpy

from colmet.metrics.base import get_hdf5_class
from colmet.metrics.base import get_counters_class

from colmet.backends.base import OutputBaseBackend, InputBaseBackend

from colmet.exceptions import JobNeedToBeDefinedError, FileAlreadyOpenWithDifferentModeError

def get_output_backend_class():
    return HDF5OutputBackend

def get_input_backend_class():
    return HDF5InputBackend

class HDF5OutputBackend(OutputBaseBackend):
    '''
    stdout backend class
    '''

    @classmethod
    def _get_backend_name(cls):
        return "hdf5"

    def __init__(self, options):
        OutputBaseBackend.__init__(self,options)
        self.stat_buffer = dict()
        
        self.jobs = {}

    def _get_job_stat(self,job_id):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobFile(self.options,job_id,'a')
        return self.jobs[job_id]

    def push(self, counters_list):
        '''
        put the metrics to the output backend
        '''
        counters_dict = dict()
        for counters in counters_list:
            job_id = counters._get_header('job_id')
            if job_id not in counters_dict:
                counters_dict[job_id] = list()
            counters_dict[job_id].append(counters)

        for (job_id,c_list) in counters_dict.iteritems():
            jobstat = self._get_job_stat(job_id)
            jobstat.append_stats(c_list)


class HDF5InputBackend(InputBaseBackend):
    
    @classmethod
    def _get_backend_name(cls):
        return "hdf5"

    
    def __init__(self, options):
        InputBaseBackend.__init__(self,options)
        
        if self.job_id_list == None or len(self.job_id_list) == 0:
            raise JobNeedToBeDefinedError

        self.jobs = {}

    def _get_job_stat(self,job_id):
        if job_id not in self.jobs:
            self.jobs[job_id] = JobFile(self.options,job_id,'r')
        return self.jobs[job_id]

    def pull(self):
        
        metrics_list = list()
        for job_id in self.job_id_list:
            jobstat = self._get_job_stat(job_id)
            job_metrics_list = jobstat.get_stats()
            metrics_list += job_metrics_list

        return metrics_list





class FileAccess(object):
    '''
    Share the access to one or several between each monitored job
    '''
    def __init__(self):
        self.hdf5_files = dict()

    def _open_hdf5_file(self,path, filemode):
        """
        Open the hdf5 file corresponding to the job.
        """
        LOG.debug("Opening the file %s" % path)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        hdf5_file = tables.openFile(path, filemode)

        return hdf5_file

    def open_file(self,path, filemode):
        if path in self.hdf5_files:
            hdf5_file = self.hdf5_files[path]
            if hdf5_file.mode != filemode:
                raise FileAlreadyOpenWithDifferentModeError(path)
        else:
            hdf5_file = self._open_hdf5_file(path,filemode)
            self.hdf5_files[path] = hdf5_file
        return hdf5_file

    def close_file_by_path(self,path):
        if path in self.hdf5_files:
            self.hdf5_files[path].close()


class JobFile(object):
    fileaccess = FileAccess()
    
    path_level = 4
    hdf5_default_filename = "counters.hdf5"

    def __init__(self,options,job_id, filemode):
        self.options = options
        self.job_id = job_id
        self.job_file = None
        self.job_filemode = filemode
        self.job_table = None
        self.job_metric_hdf5_class = None
        self.job_metric_counters_class = None
        self.job_metric_backend = None

       
        if self.job_filemode == 'r':
            LOG.debug("Reading counters in hdf5 format for job %s" % self.job_id)
            if hasattr(options,'hdf5_input_basedir'):
                self.hdf5_basedir = options.hdf5_input_basedir
            else:
                self.hdf5_basedir = "/tmp/colmet/hdf5"

            if hasattr(options,'hdf5_input_filepath') and options.hdf5_input_filepath != None:
                self.hdf5_filepath =  options.hdf5_input_filepath
            else:
                self.hdf5_filepath = "/tmp/colmet/hdf5/counters.hdf5"

            if hasattr(options,'hdf5_input_onefileperjob'):
                self.hdf5_onefileperjob = options.hdf5_input_onefileperjob
            else:
                self.hdf5_onefileperjob = False
            
        elif self.job_filemode == 'a':
            if hasattr(options,'hdf5_output_basedir'):
                self.hdf5_basedir = options.hdf5_output_basedir
            else:
                self.hdf5_basedir = "/tmp/colmet/hdf5"

            if hasattr(options,'hdf5_output_filepath') and options.hdf5_output_filepath != None:
                self.hdf5_filepath =  options.hdf5_output_filepath
            else:
                self.hdf5_filepath = "/tmp/colmet/hdf5/counters.hdf5"

            if hasattr(options,'hdf5_output_onefileperjob'):
                self.hdf5_onefileperjob = options.hdf5_output_onefileperjob
            else:
                self.hdf5_onefileperjob = False

            LOG.debug("Writing counters in hdf5 format for job %s" % self.job_id)

    def _open_job_file(self):
        """
        Open the hdf5 file corresponding to the job.
        """
        path = self._get_job_path()
        self.job_file = JobFile.fileaccess.open_file(path, self.job_filemode)

    def _init_job_file_if_needed(self,metric_backend = None):
        self._open_job_file()

        group_name = "job_%s" % self.job_id
        group_path = "/%s" % group_name
        if group_path not in self.job_file:
            root = self.job_file.root
            self.job_file.createGroup(root,group_name)
       
        table_name = "metrics"
        table_path = "%s/%s" %( group_path, table_name)
        
        if table_path not in self.job_file:
            if metric_backend == None:
                raise ValueError(
                    "The metric backend must be "
                    "defined to create the table"
                )

            self.job_metric_backend = metric_backend
            self.job_metric_hdf5_class = get_hdf5_class(metric_backend)
            self.job_metric_counters_class = get_counters_class(metric_backend)
            self.job_file.createTable(
                group_path,
                table_name,
                self.job_metric_hdf5_class.get_table_description(),
                "Metrics for the Job %s" % self.job_id
            )
            self.job_table = self.job_file.getNode(table_path)
            self.job_table.setAttr('metric_backend', metric_backend)
            self.job_table.setAttr('backend_version',HDF5_BACKEND_VERSION)
            
        else:
            self.job_table = self.job_file.getNode(table_path)
            self.job_metric_backend = self.job_table.getAttr('metric_backend')
            self.job_backend_version = self.job_table.getAttr('backend_version')
            self.job_metric_hdf5_class = get_hdf5_class(self.job_metric_backend)
            self.job_metric_counters_class = get_counters_class(self.job_metric_backend)
        



    def _get_job_path(self):
        '''
        Return the file path corresponding to a job given its job id.
        '''
        if self.hdf5_onefileperjob:
            
            i = 0
            job_id_s = str(self.job_id)
            path = ""        
            while(i < self.path_level):
                path = os.path.join(
                    path, 
                    job_id_s[i] if i < len(job_id_s) else "0"
                )
                i+=1

            path = os.path.join(self.hdf5_basedir,path)
            path = os.path.join(path,"job_%s.hdf5" % self.job_id)
        else:
            path = self.hdf5_filepath

        return path

    def append_stats(self,stats):
        if self.job_table == None:
            self._init_job_file_if_needed(stats[0].metric_backend)

        row = self.job_table.row
        for stat in stats:
            self.job_metric_hdf5_class.to_row(row,stat)
            row.append()

        self.job_table.flush()


    def get_stats(self):
        if self.job_table == None:
            self._init_job_file_if_needed()

        counters_list = list()
        for row in self.job_table.iterrows():
            counters_list.append(
                self.job_metric_hdf5_class.to_counters(row)   
            )

        return counters_list



