# Flask web interface to graph colmet data using Matplotlib/Mpld3
# Launching:
#     python colmet_web.py
# Using:
#     Point a browser to http://localhost:5000/graph/job/<job_id>/cpu
#

from flask import Flask
app = Flask(__name__)
from flask import request
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import mpld3

matplotlib.use('Agg')

# Setup the path of the hdf5 file here:
colmetfile="/scratch/bzizou/colmet/froggy.hdf5"

f = h5py.File(colmetfile, "r")

# Functions
def compute_cumul(data):
    """
        Compute cumulative time dependent data
        Take a time:data dictionnary as input and return an array of data/time_unit values
    """
    init=1
    out_data=[]
    v_prev=0
    value=0
    for t in sorted(data):
        y=data[t]
        if init==0:
            value=(y-y_prev)/(t-t_prev)
            # In case it wraps around to 0, keep the old value
            if value < 0:
                value = v_prev
            out_data.append(value)
        else:
            init=0
            out_data.append(0)
        y_prev=y
        t_prev=t
        v_prev=value
    return out_data

# Cpu/mem graphs
@app.route('/graph/job/<int:id>/cpu')
def graph_cpu(id):
    t_res=int(request.args.get('t_res', '1'))
    t_min=int(request.args.get('t_min', '0'))
    t_max=int(request.args.get('t_max', '7200'))
    # Prepare graphs
    fig_cpu = plt.figure()
    fig_mem = plt.figure()
    cpu = fig_cpu.add_subplot(111)
    mem = fig_mem.add_subplot(111)
    # Load the metrics
    metrics=f['job_'+str(id)+'/metrics']['timestamp','hostname','ac_etime','cpu_run_real_total','coremem']
    # Set the origin timestamp
    origin=metrics[0][0]
    # Get a list of uniq hosts
    hosts = set([a[1] for a in metrics])
    # For each host, create a graph of the cpu load percentagea and memory usage
    for host in hosts:
      # X axis is a number of seconds starting at 0
      x=[ a[0] for a in metrics if a[1] == host and t_min < a[0]-origin < t_max ]
      x0=x[0]
      x=[ (a - x0)/t_res for a in x ]
      # Y is the cpu and memory usage
      y_cpu=[ a[3]/a[2] for a in metrics if a[1] == host and t_min < a[0]-origin < t_max ]
      #y_mem=[ a[4]/a[2] for a in metrics if a[1] == host and t_min < a[0]-origin < t_max ]
      y_mem={ a[2]: a[4] for a in metrics if a[1] == host and t_min < a[0]-origin < t_max }
      # compute cumulative data
      y_mem=compute_cumul(y_mem)
      # Create the graphs
      cpu.plot(x,y_cpu,label=host,lw=5,alpha=0.4)
      mem.plot(x,y_mem,label=host,lw=5,alpha=0.4)
    # Print a legend
    cpu.legend()
    mem.legend()
    cpu.grid(color='lightgray', alpha=0.7)
    mem.grid(color='lightgray', alpha=0.7)
    # Return the figure 
    return mpld3.fig_to_html(fig_cpu)+mpld3.fig_to_html(fig_mem)

if __name__ == '__main__':
    app.run(debug=True)
