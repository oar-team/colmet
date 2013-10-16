# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
# USA.
#
# See the COPYING file for license information.
#
# 
# Copyright (c) 2013 Olivier Richard <olivier.richard@imag.fr>
'''
Colmet Analysis and Plotting Tools
'''

import sys
import tables
from pandas import *
import matplotlib.pyplot as plt

#
# fig2x: from http://nbviewer.ipython.org/3301035
#
from base64 import encodestring
import matplotlib
from IPython.display import display, HTML
from IPython.core.pylabtools import print_figure
from matplotlib._pylab_helpers import Gcf
from IPython.zmq.pylab.backend_inline import flush_figures

def png2x(fig):
    """render figure to 2x PNG via HTML"""
    x,y = matplotlib.rcParams['figure.figsize']
    dpi = matplotlib.rcParams['savefig.dpi']
    x2x = int(x * dpi / 2)
    y2x = int(y * dpi / 2)
    png = print_figure(fig, 'png')
    png64 = encodestring(png).decode('ascii')
    return u"<img src='data:image/png;base64,%s' width=%i height=%i/>" % (png64, x2x, y2x)

def new_flush_figures():
    try:
        for figure_manager in Gcf.get_all_fig_managers():
            display(figure_manager.canvas.figure)
    finally:
        matplotlib.pyplot.close('all')

def fig2x():
    ip = get_ipython()
    ip._post_execute.pop(flush_figures, None)

    png_formatter = ip.display_formatter.formatters['image/png']
    png_formatter.type_printers.pop(matplotlib.figure.Figure, None)

    ip.register_post_execute(new_flush_figures)
    html_formatter = ip.display_formatter.formatters['text/html']
    html_formatter.for_type(matplotlib.figure.Figure, png2x)

    ip.register_post_execute(new_flush_figures)

def figure2x():
    matplotlib.rcParams['savefig.dpi'] = 2 * matplotlib.rcParams['savefig.dpi']

#
# Main program
#

USAGE = '''%s [OPTIONS]

Analyze Colmet's traces. Output results can be textual or plots.''' % sys.argv[0]


class Doozer(object):
    pass
 
class HDF5Table(object):
    def __init__(self,h5_file_name):
        self.h5_file_name = h5_file_name
        self.h5_file = tables.File(self.h5_file_name, "r") 

    def metrics(self, node_name):
        m = self.h5_file.getNode(node_name,"metrics")
        return m.read()

    def host_metrics(self, hostname):
        pass

    def job_metrics(self, job_id):
        return self.metrics('/job_' + job_id)

    def list_jobs(self):
        return [grp._v_name for grp in self.h5_file.listNodes("/")]

    def list_job_ids(self):
        # "Job_334"[4:] -> "334"
        return [grp._v_name[4:] for grp in self.h5_file.listNodes("/")]
 
    def dataframe(self, job_id):
        return DataFrame(self.job_metrics(job_id))

#dataframe manipulation

def df_hostnames(df):
    return[h for h in df.hostname.unique()]

def df4host(df, hostname):
    return df[df.hostname==hostname]

def df_timestamp_normalize(df):
    tp_uniq = df.timestamp.unique()
    nb_doubles = len(df) - len(tp_uniq)
    print 'Nb double timestamps:' + str(nb_doubles)
    intervals = numpy.unique(tp_uniq[1:-1] - tp_uniq[0:-2])
    print 'Timestamp intervals:' + str(intervals)
    if len(intervals) == 1:
        print 'No gap in timestamps'
    else:
        print 'Nb  gaps in timestamps: ' + len(intervals)

    df_normalize = df.groupby('timestamp').first()
    return df_normalize
#
def plot_loadavg():   
    plt.figure();df0.plot( y = ['loadavg_15min', 'loadavg_1min', 'loadavg_5min']); plt.legend(loc='best')

def plot_stat_cpu():
    pass

def main():

    #plot metrics
    pass

if __name__ == '__main__':
    main()
