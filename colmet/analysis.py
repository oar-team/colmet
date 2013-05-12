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

#
# Main program
#

USAGE = '''%s [OPTIONS]

Analyze Colmet's traces. Output results can be textual or plots.''' % sys.argv[0]


class Analysis(object):
    def __init__(self,h5_file_name):
        self.h5_file_name = h5_file_name
        self.h5_file = tables.File(self.h5_file_name, "r") 

    def get_metrics(self, node_name):
        m = self.h5_file.getNode(node_name)
        return m.read()

    def get_host_metrics(self, hostname)
        h 

    def get_job_metrics(self, job_id):
        return self.get_metrics('/Job_' + job_id)


    def get_dat

def main():

    #plot metrics
    pass

if __name__ == '__main__':
    main()
