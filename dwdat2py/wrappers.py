# Copyright 2017, 2020 Tomas Nordin

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Please send bug reports or suggestions to tomasn@posteo.net or make an
# issue on github

"""Wrappers for Dewesoft's library DWDataReaderLib. Get it from
http://www.dewesoft.com/developers (need an account) and set an
environment variable `DEWELIBDIR` to the directory in which the binary
library file(s) are stored.

This module should be used with some care. Here is a typical work flow:

1.    `init()`
2.    `open_data_file('dat1')`
3.     ... other functions to get at data in dat1 ...
4.    `close_data_file()`
5.    `open_data_file('dat2')
6.     ... other functions to get at data in dat2 ...
7.    `close_data_file()` # work is done for now
8.    `de_init()`
9.     # optionally `init()` again for a new session.

"""

import ctypes as ct
import os
import platform
from collections import namedtuple
import locale
from operator import attrgetter

from . import DWDataReaderHeader as dh
from . import libdirfind, DEWELIBDIR


libdir = DEWELIBDIR or libdirfind()

libname = os.path.join(libdir, 'DWDataReaderLib')
if platform.architecture()[0] == '64bit':
    libname += '64'
if platform.system() == 'Linux':
    libname += '.so'

libname = os.path.abspath(libname)
assert(os.path.exists(libname) or os.path.exists(libname + '.dll'))

_lib = ct.cdll.LoadLibrary(libname)

# ------------------------------------------------------------------------------

_init = _lib.DWInit
_init.restype = ct.c_int
def init():
    """Must be called prior to making any other calls.

    Wraps:
        DWStatus DWInit();"""
    return _init()

# ------------------------------------------------------------------------------

_de_init = _lib.DWDeInit
_de_init.restype = ct.c_int
def de_init():
    """Must be called when done with the library.

    Wraps:
        DWStatus DWDeInit();
    """
    return _de_init()

# ------------------------------------------------------------------------------

FileInfo = namedtuple('FileInfo',
                      ('sample_rate', 'start_store_time', 'duration'))
_open_data_file = _lib.DWOpenDataFile
_open_data_file.argtypes = (ct.c_char_p, ct.POINTER(dh.DWFileInfo))
_open_data_file.restype = ct.c_int
def open_data_file(filename, fsencoding=None):
    """Open dewe data file for the lib to read.

    Return a namedtuple with members (sample_rate, start_store_time,
    duration) on success.

    filename
        The filename as a str or bytes.

    fsencoding
        The wrapped function require bytes as the file name. If
        `filename` is bytes, `fsencoding` is ignored. If `filename` is
        str and `fsencoding` is None, os.fsencode() is used to encode
        `filename` properly, else `fsencoding` is used for the
        conversion.

    Wraps
        DWStatus DWOpenDataFile(char* file_name, DWFileInfo* file_info);

    """
    info = dh.DWFileInfo()

    if not type(filename) is bytes:
        if fsencoding:
            filename = filename.encode(fsencoding)
        else:
            filename = os.fsencode(filename)

    stat = _open_data_file(filename, ct.byref(info))
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)

    return FileInfo(info.sample_rate, info.start_store_time, info.duration)

# ------------------------------------------------------------------------------

_close_data_file = _lib.DWCloseDataFile
_close_data_file.restype = ct.c_int
def close_data_file():
    """Close data file, return status code.

    Make sure a file /is/ opened, else segfault.

    Wraps:
        DWStatus DWCloseDataFile();"""
    return _close_data_file()

# ------------------------------------------------------------------------------

_get_version = _lib.DWGetVersion
_get_version.restype = ct.c_int
def get_version():
    """Return version of the dynamic link library.

    Wraps:
        int DWGetVersion();"""
    return _get_version()

# ------------------------------------------------------------------------------

_get_channel_list_count = _lib.DWGetChannelListCount
_get_channel_list_count.restype = ct.c_int
def get_channel_list_count():
    """Return the number of channels.

    Wraps:
        int DWGetChannelListCount();"""

    num = _get_channel_list_count()
    if num == -1:
        raise RuntimeError('get_channel_list_count returned -1')
    return num

# ------------------------------------------------------------------------------

Channel = namedtuple('Channel', ('index', 'name', 'unit', 'description',
                                 'color', 'array_size', 'data_type'))
_get_channel_list = _lib.DWGetChannelList
_get_channel_list.argtypes = (ct.POINTER(dh.DWChannel),)
_get_channel_list.restype = ct.c_int
def get_channel_list(encoding=None):
    """Return a list with namedtuples with info on each channel.

    `encoding` if given is used to decode the bytes retreived as the
    `name`, `unit` and `description` components of the channel info. If
    not given, `locale.getpreferredencding()` is used.

    Wraps
        DWStatus DWGetChannelList(DWChannel* channel_list);

    """

    ch_list = (dh.DWChannel * get_channel_list_count())()
    stat = _get_channel_list(ch_list)
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    encoding = encoding or locale.getpreferredencoding()
    res = []
    for ch in ch_list:
        res.append(Channel(ch.index, ch.name.decode(encoding),
                           ch.unit.decode(encoding),
                           ch.description.decode(encoding),
                           ch.color, ch.array_size, ch.data_type))
    return res

# ------------------------------------------------------------------------------

_get_reduced_values_count = _lib.DWGetReducedValuesCount
_get_reduced_values_count.argtypes = (ct.c_int, ct.POINTER(ct.c_int),
                                      ct.POINTER(ct.c_double))
_get_reduced_values_count.restype = ct.c_int
def get_reduced_values_count(ch_index):
    """Return the number of samples for channel with given index.

    Return a two-tuple (count, seconds), seconds being the sample time
    resolution.

    Wraps:
        DWStatus DWGetReducedValuesCount(int ch_index, int* count,
                                         double* block_size);
    """
    count = ct.c_int()
    seconds = ct.c_double()
    stat = _get_reduced_values_count(ch_index, ct.byref(count),
                                     ct.byref(seconds))
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    return (count.value, seconds.value)

# ------------------------------------------------------------------------------

_get_reduced_values = _lib.DWGetReducedValues
_get_reduced_values.argtypes = (ct.c_int, ct.c_int, ct.c_int,
                                ct.POINTER(dh.DWReducedValue))
_get_reduced_values.restype = ct.c_int
def get_reduced_values(ch_index, position, count):
    """Get channel reduced data.

    Data records are (time_stamp, ave, min, max, rms), starting at
    position position with the count count.

    Wraps:
        DWStatus DWGetReducedValues(int ch_index, int position,
                                    int count, struct DWReducedValue* data);

    """

    data = (dh.DWReducedValue * count)()
    stat = _get_reduced_values(ch_index, position, count, data)
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    return [(v.time_stamp, v.ave, v.min, v.max, v.rms) for v in data]

# ------------------------------------------------------------------------------

def channel_reduced(channel, reduction, encoding=None):
    """Return a flat list of data for channel reduced to reduction.

    Parameters
    ----------

    channel : int or str
        Either the channel index or the channel name.

    reduction : int
        One of the following
        time_stamp = 0
        ave = 1
        min = 2
        max = 3
        rms = 4

    encoding : str
        encoding to pass to `get_channel_list()`, which see.

    Wraps:
        Nothing explicit. This is a support function to simplify getting
        reduced data from a channel.

    """

    index = None

    getter = type(channel) is int and attrgetter('index') or attrgetter('name')

    for ch in get_channel_list(encoding):
        if getter(ch) == channel:
            index = ch.index
            break
    else:                       # no break
        raise ValueError(channel, 'not found in data')

    cnt = get_reduced_values_count(index)[0]
    return [rec[reduction] for rec in get_reduced_values(index, 0, cnt)]
