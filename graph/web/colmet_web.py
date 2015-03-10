# Flask web interface to graph colmet data using Matplotlib/Mpld3
# Launching:
#     python colmet_web.py
# Using:
#     Point a browser to http://localhost:5000/graph/job/<job_id>
#

from flask import Flask
app = Flask(__name__)
from flask import request
from flask import render_template
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

# Cpu/mem/io graphs
@app.route('/graph/job/<int:id>')
def graph(id):
    # Read parameters
    t_res=int(request.args.get('t_res', '1'))
    t_min=int(request.args.get('t_min', '0'))
    t_max=int(request.args.get('t_max', '7200'))
    # Prepare graphs
    fig={}
    graph={}
    for g in [ 'cpu','mem','read','write']:
        fig[g] = plt.figure(figsize=(9,5))
        graph[g] = fig[g].add_subplot(111)
    # Load the metrics
    metrics=f['job_'+str(id)+'/metrics']['timestamp','hostname','ac_etime','cpu_run_real_total','coremem','read_bytes','write_bytes']
    # Set the origin timestamp
    origin=metrics[0][0]
    # Get a list of uniq hosts
    hosts = set([a[1] for a in metrics])
    # For each host
    for host in hosts:
      # X axis is a number of seconds starting at 0
      x=[ a[0] for a in metrics if a[1] == host and t_min < a[0]-origin < t_max ]
      x0=x[0]
      x=[ (a - x0)/t_res for a in x ]
      # Cpu
      y_cpu=[ 1.0*a[3]/a[2]/1000 for a in metrics if a[1] == host and t_min < a[0]-origin < t_max ]
      graph['cpu'].plot(x,y_cpu,label=host,lw=5,alpha=0.4)
      # Memory
      y_mem={ a[2]: 1.0*a[4]/1024 for a in metrics if a[1] == host and t_min < a[0]-origin < t_max }
      y_mem=compute_cumul(y_mem)
      graph['mem'].plot(x,y_mem,label=host,lw=5,alpha=0.4)
      graph['mem'].set_ylabel('rss (GBytes)')
      # Read/Write
      y_read={ a[0]: 1.0*a[5]/1024/1024 for a in metrics if a[1] == host and t_min < a[0]-origin < t_max }
      y_read=compute_cumul(y_read)
      graph['read'].plot(x,y_read,label=host,lw=5,alpha=0.4)
      graph['read'].set_ylabel('Read (MBytes/s)')
      y_write={ a[0]: 1.0*a[6]/1024/1024 for a in metrics if a[1] == host and t_min < a[0]-origin < t_max }
      y_write=compute_cumul(y_write)
      graph['write'].plot(x,y_write,label=host,lw=5,alpha=0.4)
      graph['write'].set_ylabel('Write (MBytes/s)')
    # Print a legend and generate html
    html={}
    for g in [ 'cpu','mem','read','write']:
        graph[g].legend()
        graph[g].grid(color='lightgray', alpha=0.7)
        graph[g].set_xlabel('time (s)')
        html[g]=mpld3.fig_to_html(fig[g])
    # Rendering 
    return render_template('show_job_graphs.html', graph=html)
    #return mpld3.fig_to_html(fig['cpu'])+mpld3.fig_to_html(fig['mem'])+mpld3.fig_to_html(fig['read'])+mpld3.fig_to_html(fig['write'])

if __name__ == '__main__':
    app.run(debug=True)
