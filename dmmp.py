"""
Python API for multipath-tools
"""
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
import ctypes
import sys
import struct


_API_VERSION_MAJOR = 0

_IPC_ADDR = "\0/org/kernel/linux/storage/multipathd"

_IPC_LEN_SIZE = ctypes.sizeof(ctypes.c_ssize_t(0))


def _len_to_ssize_t_bytes(len_value):
    try:
        return struct.pack("n", len_value)
    except struct.error:
        h = "%x" % len_value
        s = ("0" * (len(h) % 2) + h).zfill(_IPC_LEN_SIZE * 2).decode("hex")
        if sys.byteorder == "little":
            s = s[::-1]
        return bytearray(s)


def _bytes_to_len(len_bytes):
    try:
        return struct.unpack("n", len_bytes)[0]
    except struct.error:
        if sys.byteorder == "little":
            len_bytes = len_bytes[::-1]
        return int(len_bytes.encode("hex"), 16)


class DMMP_path(object):
    """
    DMMP_pathgroup is the abstraction of path in multipath-tools.
    """
    def __init__(self, path):
        """
        Internal function. For mpaths_get() only.
        """
        for key, value in path.items():
            setattr(self, "_%s" % key, value)
        self._status = DMMP_path._status_str_to_enum(self._chk_st)

    STATUS_UNKNOWN = 0
    STATUS_DOWN = 2
    STATUS_UP = 3
    STATUS_SHAKY = 4
    STATUS_GHOST = 5
    STATUS_PENDING = 6
    STATUS_TIMEOUT = 7
    STATUS_DELAYED = 9

    _STATUS_CONV = {
        STATUS_UNKNOWN: "undef",
        STATUS_UP: "ready",
        STATUS_DOWN: "faulty",
        STATUS_SHAKY: "shaky",
        STATUS_GHOST: "ghost",
        STATUS_PENDING: "i/o pending",
        STATUS_TIMEOUT: "i/o timeout",
        STATUS_DELAYED: "delayed",
    }

    @staticmethod
    def _status_str_to_enum(status_str):
        for key, value in DMMP_path._STATUS_CONV.items():
            if value == status_str:
                return key
        return DMMP_path.STATUS_UNKNOWN

    @staticmethod
    def status_to_str(status):
        """
        Usage:
            Convert status integer to human readable string:
                DMMP_path.STATUS_UNKNOWN:       "undef"
                DMMP_path.STATUS_UP:            "ready"
                DMMP_path.STATUS_DOWN:          "faulty"
                DMMP_path.STATUS_SHAKY:         "shaky"
                DMMP_path.STATUS_GHOST:         "ghost"
                DMMP_path.STATUS_PENDING:       "i/o pending"
                DMMP_path.STATUS_TIMEOUT:       "i/o timeout"
                DMMP_path.STATUS_DELAYED:       "delayed"
        Parameters:
            status              Integer. DMMP_path.status
        Returns:
            status_str          String.
        Exception:
            ValueError          If got illegal status.
        """
        try:
            return DMMP_path._STATUS_CONV[status]
        except KeyError:
            return ValueError("Invalid path status %d" % status)

    @property
    def blk_name(self):
        """
        String.  Block name of current path. Examples: "sda", "nvme0n1".
        """
        return self._dev

    @property
    def status(self):
        """
        Integer. Status of current path. Possible values are:
        * DMMP_path.STATUS_UNKNOWN
            Unknown status.
        * DMMP_path.STATUS_DOWN
            Path is down and you shouldn't try to send commands to it.
        * DMMP_path.STATUS_UP
            Path is up and I/O can be sent to it.
        * DMMP_path.STATUS_SHAKY
            Only emc_clariion checker when path not available for "normal"
            operations.
        * DMMP_path.STATUS_GHOST
            Only hp_sw and rdac checkers.  Indicates a "passive/standby" path
            on active/passive HP arrays. These paths will return valid answers
            to certain SCSI commands (tur, read_capacity, inquiry, start_stop),
            but will fail I/O commands.
            The path needs an initialization command to be sent to it in order
            for I/Os to succeed.
        * DMMP_path.STATUS_PENDING
            Available for all async checkers when a check IO is in flight.
        * DMMP_path.STATUS_TIMEOUT
            Only tur checker when command timed out.
        * DMMP_path.STATUS_DELAYED
            If a path fails after being up for less than delay_watch_checks
            checks, when it comes back up again, it will not be marked as up
            until it has been up for delay_wait_checks checks. During this
            time, it is marked as "delayed".
        """
        return self._status

    def __str__(self):
        return "%s|%s" % (self.blk_name, DMMP_path.status_to_str(self.status))


class DMMP_pathgroup(object):
    """
    DMMP_pathgroup is the abstraction of path group in multipath-tools.
    """
    def __init__(self, pg):
        """
        Internal function. For mpaths_get() only.
        """
        self._paths = []
        for key, value in pg.items():
            if key == "paths":
                for path in pg["paths"]:
                    self._paths.append(DMMP_path(path))
            else:
                setattr(self, "_%s" % key, value)

        self._status = DMMP_pathgroup._status_str_to_enum(self._dm_st)

    STATUS_UNKNOWN = 0
    STATUS_ENABLED = 1
    STATUS_DISABLED = 2
    STATUS_ACTIVE = 3

    _STATUS_CONV = {
        STATUS_UNKNOWN: "undef",
        STATUS_ENABLED: "enabled",
        STATUS_DISABLED: "disabled",
        STATUS_ACTIVE: "active",
    }

    @staticmethod
    def _status_str_to_enum(status_str):
        for key, value in DMMP_pathgroup._STATUS_CONV.items():
            if value == status_str:
                return key
        return DMMP_pathgroup.STATUS_UNKNOWN

    @staticmethod
    def status_to_str(status):
        """
        Usage:
            Convert status integer to human readable string:
                DMMP_pathgroup.STATUS_UNKNOWN:       "undef"
                DMMP_pathgroup.STATUS_ENABLED:       "enabled"
                DMMP_pathgroup.STATUS_DISABLED:      "disabled"
                DMMP_pathgroup.STATUS_ACTIVE:        "active"
        Parameters:
            status              Integer. DMMP_pathgroup.status
        Returns:
            status_str          String.
        Exception:
            ValueError          If got illegal status.
        """
        try:
            return DMMP_pathgroup._STATUS_CONV[status]
        except KeyError:
            return ValueError("Invalid path group status %d" % status)

    @property
    def id(self):
        """
        Integer. Group ID of current path group. Could be used for
        switching active path group.
        """
        return self._group

    @property
    def status(self):
        """
        Integer. Status of current path group. Possible values are:
        * DMMP_pathgroup.STATUS_UNKNOWN
            Unknown status
        * DMMP_pathgroup.STATUS_ENABLED
            Standby to be active
        * DMMP_pathgroup.STATUS_DISABLED
            Disabled due to all path down
        * DMMP_pathgroup.STATUS_ACTIVE
            Selected to handle I/O
        """
        return self._status

    @property
    def priority(self):
        """
        Integer. Priority of current path group. The enabled path group with
        highest priority will be next active path group if active path group
        down.
        """
        return self._pri

    @property
    def selector(self):
        """
        String. Selector of current path group. Path group selector determines
        which path in active path group will be use to next I/O.
        """
        return self._selector

    @property
    def paths(self):
        """
        List of DMMP_path objects.
        """
        return self._paths

    def __str__(self):
        return "%s|%s|%d" % (
            self.id, DMMP_pathgroup.status_to_str(self.status), self.priority)


class DMMP_mpath(object):
    """
    DMMP_mpath is the abstraction of mpath(aka. map) in multipath-tools.
    """
    def __init__(self, mpath):
        """
        Internal function. For mpaths_get() only.
        """
        self._path_groups = []
        for key, value in mpath.items():
            if key == "path_groups":
                for pg in mpath["path_groups"]:
                    self._path_groups.append(DMMP_pathgroup(pg))
            else:
                setattr(self, "_%s" % key, value)

    @property
    def wwid(self):
        """
        String. WWID of current mpath.
        """
        return self._uuid

    @property
    def name(self):
        """
        String. Name(alias) of current mpath.
        """
        return self._name

    @property
    def path_groups(self):
        """
        List of DMMP_mpath objects.
        """
        return self._path_groups

    def __str__(self):
        return "'%s'|'%s'" % (self.wwid, self.name)


def _ipc_exec(s, cmd):
    buff = _len_to_ssize_t_bytes(len(cmd) + 1) + bytearray(cmd, 'utf-8') + \
        b'\0'
    s.sendall(buff)
    buff = s.recv(_IPC_LEN_SIZE)
    if not buff:
        return ""
    output_len = _bytes_to_len(buff)
    output = s.recv(output_len).decode("utf-8")
    return output.strip('\x00')


def mpaths_get():
    """
    Usage:
        Query all multipath devices.
    Parameters:
        void
    Returns:
        [DMMP_mpath,]       List of DMMP_mpath objects.
    """
    rc = []
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(60)
    s.connect(_IPC_ADDR)
    json_str = _ipc_exec(s, "show maps json")
    s.close()
    if len(json_str) == 0:
        return rc
    all_data = json.loads(json_str)
    if all_data["major_version"] != _API_VERSION_MAJOR:
        raise exception("incorrect version")

    for mpath in all_data["maps"]:
        rc.append(DMMP_mpath(mpath))
    return rc
