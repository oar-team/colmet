#!/bin/env python
# Simple example script to graph cpu percentages of a given job
# from an hdf5 colmet file
#
# Example usage:
# [bzizou@froggy1 colmet]$ ./colmet_hdf5_graph.py 5251912
#  Loading hdf5 file...
#  Loading metrics...
#  Computing...
#  Generating 5251912_cpu_count.png...

# Setup the path of the hdf5 file here:
colmetfile = "/scratch/bzizou/colmet/froggy.hdf5"

import sys
import h5py
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

job = sys.argv[1]

print("Loading hdf5 file...")
f = h5py.File(colmetfile, "r")

# Liste des meta-data
# for name,value in f['job_5254532/metrics'].attrs.iteritems():
#     print name,":",value

# Load the metrics
print('Loading metrics...')
fields = ('timestamp', 'hostname', 'ac_etime', 'cpu_run_real_total')
metrics = f['job_' + job + '/metrics'][fields]

# Get a list of uniq hosts
hosts = set([a[1] for a in metrics])

# For each host, create a graph of the cpu load percentage
print('Computing...')
for host in hosts:
    x = [a[0] for a in metrics if a[1] == host]
    y = [a[3] / a[2] / 10 for a in metrics if a[1] == host]
    plt.plot(x, y, label=host)

# Print a legend
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)

# Generate the output
output_file = job + '_cpu_count.png'
print('Generating ' + output_file + '...')
plt.savefig(output_file)
