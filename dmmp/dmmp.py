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

import json
import socket
import struct

_IPC_ADDR = "\0/org/kernel/linux/storage/multipathd"

_HDR_LEN = 8

_API_VERSION_MAJOR = 0

class DMMP_mpath(object):
    def __init__(self, mpath):
        self.wwid = mpath["uuid"]
        self.name = mpath["name"]
        self._pgs = mpath["path_groups"]
        print(self._pgs)

    def __str__(self):
        return "'%s'|'%s'" % (self.wwid, self.name)

def _ipc_exec(s, cmd):
    buff = struct.pack("=Q", len(cmd) + 1) + bytearray(cmd, 'utf-8') + b'\0'
    s.sendall(buff)
    output_len = struct.unpack("=Q", s.recv(_HDR_LEN))[0]
    output = s.recv(output_len).decode("utf-8")
    return output.strip('\x00')

def mpaths_get():
    rc = []
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(60)
    s.connect(_IPC_ADDR)
    json_str = _ipc_exec(s, "show maps json")
    s.close()
    all_data = json.loads(json_str)
    if all_data["major_version"] != _API_VERSION_MAJOR:
        raise exception("incorrect version")

    for mpath in all_data["maps"]:
        rc.append(DMMP_mpath(mpath))
    return rc
