#!/usr/bin/env python
#
# colmet: Display/Collect ressources usage of tasks (cpuset,cgroup)
#
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
# Copyright (c) 2012 Philippe Le Brouster <philippe.le-brouster@imag.fr>
'''
colmet_node retrieve information about job (task/process/cgroup/etc.) 
using the given input backend and send them using the output backend.
'''
import sys
import logging

from colmet.ui import main
from colmet.exceptions import Error

try:
    main()
except KeyboardInterrupt:
    pass
except Error as err:
    err.show()
    sys.exit(1)
except Exception as err:
    MSG = "Error not handled '%s'" % err.__class__.__name__
    logging.critical(MSG)
    if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
        print repr(err)
    raise 

sys.exit(0)
