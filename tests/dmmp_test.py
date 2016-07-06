#!/usr/bin/python
#
# Copyright (C) 2016 Red Hat, Inc.
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; If not, see <http://www.gnu.org/licenses/>.
#
# Author: Gris Ge <fge@redhat.com>

import os, sys

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(_CURRENT_DIR))

import dmmp

for mpath in dmmp.mpaths_get():
    print("Got mpath: wwid '%s', name '%s'" % (mpath.wwid, mpath.name))
    for pg in mpath.path_groups:
        print("\tGot path group: id '%d', priority '%d', status '%d(%s)', "
              "selector '%s'" %
              (pg.id, pg.priority, pg.status,
               dmmp.DMMP_pathgroup.status_to_str(pg.status), pg.selector))

        for p in pg.paths:
            print("\t\tGot path: blk_name '%s', status '%d(%s)'" %
                  (p.blk_name, p.status,
                   dmmp.DMMP_path.status_to_str(p.status)))
