Colmet CHANGELOG
================

version 0.3.0:
--------------

- Divided colmet package into three parts
  - colmet-node : Retrieve data from taskstats and procstats and send to
    collectors with ZeroMQ
  - colmet-collector : A collector that stores data received by ZeroMQ in a
    hdf5 file
  - colmet-common : Common colmet part.
- Added some parameters of ZeroMQ backend to prevent a memory overflow
- Simplified the command line interface
- Dropped rrd backend because it is not yet working
- Added ``--buffer-size`` option for collector to define the maximum number of
  counters that colmet should queue in memory before pushing it to output
  backend
- Handled SIGTERM and SIGINT to terminate colmet properly

version 0.2.0:
--------------

- Added options to enable hdf5 compression
- Support for multiple job by cgroup path scanning
- Used Inotify events for job list update
- Don't filter packets if no job_id range was specified, especially with zeromq
  backend
- Waited the cgroup_path folder creation before scanning the list of jobs
- Added procstat for node monitoring through fictive job with 0 as identifier
- Used absolute time take measure and not delay between measure, to avoid the
  drift of measure time
- Added workaround when a newly cgroup is created without process in it
  (monitoring is suspended upto one process is launched)


version 0.0.1:
--------------

- Conception
