Colmet - Collecting metrics about jobs running in a distributed environnement

Introduction:
-------------

Colmet is a monitoring tool to collect metrics about jobs running in a
distributed environnement, especially for gathering metrics on clusters and
grids. It provides currently several backends :
    - taskstats: fetch task metrics from the linux kernel
    - stdout: display the metrics on the terminal
    - zeromq: transport the metrics across the network
    - hdf5: store the metrics on the filesystem

Installation:
-------------

Requirements
~~~~~~~~~~~~

* a Linux kernel that supports
   - Taskstats

* Python Version 2.7 or newer
   - python-zmq 2.2.0 or newer
   - python-tables 2.3.1 or newer
   - python-pyinotify 0.9.3-2 or newer

Installation
~~~~~~~~~~~~

You can install, upgrade, uninstall colmet with these commands::

  $ pip install [--user] colmet
  $ pip install [--user] --upgrade colmet
  $ pip uninstall colmet

Or from git (last development version)::

  $ pip install [--user] git+https://github.com/oar-team/colmet.git

Or if you already pulled the sources::

  $ pip install [--user] path/to/sources

Or if you don't have pip::

  $ easy_install colmet

Usage:
------

for the nodes :

    sudo colmet-node -vvv --zeromq-uri tcp://127.0.0.1:5556

for the collector :

    colmet-collector -vvv --zeromq-bind-uri tcp://127.0.0.1:5556 --hdf5-filepath /data/colmet.hdf5 --hdf5-complevel 9

You will see the number of counters retrieved in the debug log.


For more information, please refer to the help of theses scripts (--help)

Licensing:
----------

This product is distributed under the GNU General Public License Version2.
Please read through the file LICENSE for more information about our license.
