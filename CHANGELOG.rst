Colmet CHANGELOG
================

version 0.2.0:
--------------

* Divided colmet package into three parts
  - colmet-node : Retrieve data from taskstats and procstats and send to collectors with ZeroMQ
  - colmet-hdf5-collector : A collector that stores data received by ZeroMQ in a hdf5 file
  - colmet-common : Common colmet part.
* Added some parameters of ZeroMQ backend to prevent a memory overflow
* Simplified the command line interface


version 0.0.1:
--------------

* Conception
