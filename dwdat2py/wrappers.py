#! /usr/bin/env python
#! -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2017 Tomas Nordin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Please send bug reports or suggestions to tomasn@posteo.net or make an issue
# on github

"""Wrappers for Dewesoft's library DWDataReaderLib. Get it from
http://www.dewesoft.com/developers (need an account) and set an
environment variable `DEWELIBDIR` to the directory in which the binary
library file(s) are stored.

This module should be used with some care. Here is a typical workflow:

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
import os, platform
from collections import namedtuple

from . import dwheader as dh

libdir = os.getenv('DEWELIBDIR')
if libdir is None:
    raise EnvironmentError('DEWELIBDIR environment variable not found')

libname = os.path.join(libdir, 'DWDataReaderLib')
if platform.architecture()[0] == '64bit':
    libname += '64'
if platform.system() == 'Linux':
    libname += '.so'

libname = os.path.abspath(libname)
assert(os.path.exists(libname))

_lib = ct.cdll.LoadLibrary(libname)

# ------------------------------------------------------------------------------

_init = _lib.DWInit
_init.restype = ct.c_int
def init():
    """Must be called prior to making any other calls.

    oWraps:
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
def open_data_file(filename):
    """Open dewe data file for the lib to read.

    Return a namedtuple with members (sample_rate, start_store_time,
    duration) on success.

    Wraps:
        DWStatus DWOpenDataFile(char* file_name, DWFileInfo* file_info);

    """
    info = dh.DWFileInfo()
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
def get_channel_list():
    """Return a list with namedtuples with info on each channel.

    Wraps:
        DWStatus DWGetChannelList(DWChannel* channel_list);"""

    ch_list = (dh.DWChannel * get_channel_list_count())()
    stat = _get_channel_list(ch_list)
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    res = []
    for ch in ch_list:
        res.append(Channel(ch.index, ch.name, ch.unit, ch.description,
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

def channel_reduced(channel, reduction):
    """Return a flat list of data for channel reduced to reduction.

    Parameters
    ----------

    channel : int or string
        Either the channel index or the channel name.

    reduction : int
        One of the following
        time_stamp = 0
        ave = 1
        min = 2
        max = 3
        rms = 4

    Wraps:
        Nothing explicit. This is a support function to simplify getting
        reduced data from a channel.

    """

    index = None
    for ch in get_channel_list():
        if ch.name == channel or ch.index == channel:
            index = ch.index
            break
    else:                       # no break
        raise ValueError(channel)

    cnt = get_reduced_values_count(index)[0]
    return [rec[reduction] for rec in get_reduced_values(index, 0, cnt)]


################## debug code: ######################

# print 'trying my functions..'
# stat = init()
# print 'stat of init:', stat, dh.DWStatus(stat).name
# print 'version:', get_version()
# fi = open_data_file(u'/home/tomas/broms/setup_0001.dxd')
# print fi
# print 'number of channels:', get_channel_list_count()
# ch_list = get_channel_list()
# for ch in ch_list:
#     print ch
#     count_res = get_reduced_values_count(ch.index)
#     print count_res
#     print get_reduced_values(ch.index, 0, count_res[0])
# stat = close_data_file()
# print 'stat of close_data_file', stat, dh.DWStatus(stat).name
# stat = de_init()
# print 'stat of de_init', stat, dh.DWStatus(stat).name
