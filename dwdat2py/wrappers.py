# Copyright 2017, 2020-2021 Tomas Nordin

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
from . import libdirfind

libdir = libdirfind()

libname = os.path.join(libdir, 'DWDataReaderLib')
if platform.architecture()[0] == '64bit':
    libname += '64'
if platform.system() == 'Linux':
    libname += '.so'

libname = os.path.abspath(libname)
assert(os.path.exists(libname) or os.path.exists(libname + '.dll'))

_lib = ct.cdll.LoadLibrary(libname)

# --------------------------------------------------------------------

_init = _lib.DWInit
_init.restype = ct.c_int
def init():
    """Must be called prior to making any other calls.

    Wraps:
        DWStatus DWInit();"""
    return _init()

# --------------------------------------------------------------------

_de_init = _lib.DWDeInit
_de_init.restype = ct.c_int
def de_init():
    """Must be called when done with the library.

    Wraps:
        DWStatus DWDeInit();
    """
    return _de_init()

# --------------------------------------------------------------------

_get_storing_type = _lib.DWGetStoringType
_get_storing_type.restype = ct.c_int
def get_storing_type():
    """Return the storing type of the data file.

    One of the following integers:

    0 --> ST_ALWAYS_FAST
    1 --> ST_ALWAYS_SLOW
    2 --> ST_FAST_ON_TRIGGER
    3 --> ST_FAST_ON_TRIGGER_SLOW_OTH

    A STORING_TYPE dict is provided by this module.

    Wraps:
        int DWGetStoringType();
        (not documented)

    """

    return _get_storing_type()

# --------------------------------------------------------------------

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

# --------------------------------------------------------------------

_close_data_file = _lib.DWCloseDataFile
_close_data_file.restype = ct.c_int
def close_data_file():
    """Close data file, return status code.

    Make sure a file /is/ opened, else segfault.

    Wraps:
        DWStatus DWCloseDataFile();"""
    return _close_data_file()

# --------------------------------------------------------------------

_get_version = _lib.DWGetVersion
_get_version.restype = ct.c_int
def get_version():
    """Return version of the dynamic link library.

    Wraps:
        int DWGetVersion();"""
    return _get_version()

# --------------------------------------------------------------------

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

# --------------------------------------------------------------------

Channel = namedtuple('Channel', ('index', 'name', 'unit', 'description',
                                 'color', 'array_size', 'data_type'))
_get_channel_list = _lib.DWGetChannelList
_get_channel_list.argtypes = (ct.POINTER(dh.DWChannel),)
_get_channel_list.restype = ct.c_int
def get_channel_list(encoding=None):
    """Return a list with namedtuples with info on each channel.

    `encoding` if given is used to decode the bytes retreived as the
    `name`, `unit` and `description` components of the channel info. If
    not given, `locale.getpreferredencoding()` is used.

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

# --------------------------------------------------------------------

_get_channel_factors = _lib.DWGetChannelFactors
_get_channel_factors.argtypes = (ct.c_int, ct.POINTER(ct.c_double),
                                 ct.POINTER(ct.c_double))
_get_channel_factors.restype = ct.c_int
def get_channel_factors(ch_index):
    """
    Return channel scale and offset as (scale, offset).

    Wraps
        DWStatus DWGetChannelFactors(int ch_index, double* scale,
                                     double* offset);

    """
    scale, offset = ct.c_double(), ct.c_double()
    stat = _get_channel_factors(ch_index, ct.byref(scale), ct.byref(offset))
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    return (scale.value, offset.value)

# --------------------------------------------------------------------

_get_channel_props = _lib.DWGetChannelProps
_get_channel_props.argtypes = (ct.c_int, ct.c_int, ct.c_voidp,
                               ct.POINTER(ct.c_int))
_get_channel_props.restype = ct.c_int
def get_channel_props(ch_index, ch_prop, encoding=None):
    """Return the property specifed by `ch_prop`.

    `ch_prop` shall be one of the integers listed below. It is not
    necessary to make preparatory calls to length variants. The two last
    "commented" options are not supported by this function.

    `encoding` is used to decode the bytes returned from the wrapped
    function when `ch_prop` is 7 or 9. `locale.getpreferredencoding()`
    is used as a default.

    DW_DATA_TYPE = 0,            # get data type
    DW_DATA_TYPE_LEN_BYTES = 1,  # get length of data type in bytes
    DW_CH_INDEX = 2,             # get channel index
    DW_CH_INDEX_LEN = 3,         # get length of channel index
    DW_CH_TYPE = 4,              # get channel type
    DW_CH_SCALE = 5,             # get channel scale
    DW_CH_OFFSET = 6,            # get channel offset
    DW_CH_XML = 7,               # get channel XML
    DW_CH_XML_LEN = 8,           # get length of channel XML
    DW_CH_XMLPROPS = 9,          # get channel XML properties
    DW_CH_XMLPROPS_LEN = 10,     # get length of channel XML properties
    # DW_CH_CUSTOMPROPS = 11,      # get channel XML custom properties
    # DW_CH_CUSTOMPROPS_COUNT = 12 # get length of channel XML custom

    Wraps
        DWStatus DWGetChannelProps(int ch_index, enum DWChannelProps ch_prop,
                                   void* buffer, int* max_len);

    """

    P = dh.DWChannelProps
    p = P(ch_prop)
    # default prep
    maxlen = ct.c_int(ct.sizeof(ct.c_int))
    pbuffer = ct.create_string_buffer(maxlen.value)
    encoding = encoding or locale.getpreferredencoding()

    if p.value in (0, 1, 2, 3, 4, 8, 10):  # int return types
        stat = _get_channel_props(ch_index, p.value, pbuffer,
                                  ct.byref(maxlen))
        if stat != 0:
            raise RuntimeError(dh.DWStatus(stat).name)
        return ct.cast(pbuffer, ct.POINTER(ct.c_int)).contents.value

    elif p.value in (5, 6):  # double return types
        maxlen = ct.c_int(ct.sizeof(ct.c_double))
        pbuffer = ct.create_string_buffer(maxlen.value)
        stat = _get_channel_props(ch_index, p.value, pbuffer,
                                  ct.byref(maxlen))
        if stat != 0:
            raise RuntimeError(dh.DWStatus(stat).name)
        return ct.cast(pbuffer, ct.POINTER(ct.c_double)).contents.value

    elif p.value == 7:     # char buffer (xml) return type
        stat = _get_channel_props(ch_index, 8, pbuffer, ct.byref(maxlen))
        if stat != 0:
            raise RuntimeError(dh.DWStatus(stat).name)

        strlen = ct.cast(pbuffer, ct.POINTER(ct.c_int)).contents.value
        maxlen = ct.c_int(strlen + 1)
        # segfaults seen when strlen has been 0, escape that
        if maxlen.value < 2:
            return b''
        pbuffer = ct.create_string_buffer(maxlen.value)
        stat = _get_channel_props(ch_index, p.value, pbuffer,
                                  ct.byref(maxlen))
        if stat != 0:
            raise RuntimeError(dh.DWStatus(stat.name))

        return pbuffer.value.decode(encoding)

    elif p.value == 9:     # char buffer (xml) return type
        stat = _get_channel_props(ch_index, 10, pbuffer, ct.byref(maxlen))
        if stat != 0:
            raise RuntimeError(dh.DWStatus(stat).name)

        strlen = ct.cast(pbuffer, ct.POINTER(ct.c_int)).contents.value
        maxlen = ct.c_int(strlen + 1)
        # segfaults seen when strlen has been 0, escape that
        if maxlen.value < 2:
            return b''
        pbuffer = ct.create_string_buffer(maxlen.value)
        stat = _get_channel_props(ch_index, p.value, pbuffer,
                                  ct.byref(maxlen))
        if stat != 0:
            raise RuntimeError(dh.DWStatus(stat).name)

        return pbuffer.value.decode(encoding)

# --------------------------------------------------------------------

_get_scaled_samples_count = _lib.DWGetScaledSamplesCount
_get_scaled_samples_count.argtypes = (ct.c_int,)
_get_scaled_samples_count.restype = ct.c_longlong
def get_scaled_samples_count(ch_index):
    """Return the number of samples for channel with given index.

    Wraps
        __int64 DWGetScaledSamplesCount(int ch_index);

    """

    return _get_scaled_samples_count(ch_index)

# --------------------------------------------------------------------

# DWStatus DWGetScaledSamples(int ch_index, __int64 position, int count,
# double* data, double* time_stamp);
# Parameters:
#       ch_index – ch. identifier
#       position – offset position; the first sample has position 0
#       count – number of samples to be returned
#       data – channel values; variable should be allocated (double
# precision)
#       time_stamp – channel time stamps; variable should be allocated (in
# seconds)

# Return value: See above enumerator
# Description: This function returns scaled data from the direct buffer.

_get_scaled_samples = _lib.DWGetScaledSamples
_get_scaled_samples.argtypes = (ct.c_int, ct.c_longlong, ct.c_int,
                                ct.POINTER(ct.c_double),
                                ct.POINTER(ct.c_double))
_get_scaled_samples.restype = ct.c_int
def get_scaled_samples(ch_index, position, count, array_size=1):
    """Return "full speed" (time_stamp, data) for channel `ch_index`.

    ch_index : int
        The channel enumeration.

    position : int
        offset position, the first sample has position 0.

    count : int
        Number of samples to be returned

    array_size : int
        As given for respective channel by `get_channel_list()`
        (Channel.array_size). This shall be 1 if the channel is not an
        array channel.

    Wraps
        DWStatus DWGetScaledSamples(int ch_index, __int64 position,
                                    int count, double* data,
                                    double* time_stamp);

    Note
        To get an array out of the data returned, if channel is an
        array channel (Channel.array_size > 1) and if the number of
        arrays > 1 (get_scaled_samples_count() > 1), do this

        startpos = n * array_size
        array_n = data[startpos:startpos + array_size]

        # 0 <= n < get_scaled_samples_count(ch_index)

        n is the zero-based enumeration of the arrays (referring to
        one of multiple arrays).

        To get the one time_stamp element for the array, do time[n],
        where time is returned from this function.

        The above advice assumes this function is called the same way
        with the array channel as with a non-array channel:

        position = 0
        count = get_scaled_samples_count(ch_index)
        array_size = Channel.array_size

    """

    data = (ct.c_double * (count * array_size))()  # (c_double_Array_...)
    time = (ct.c_double * (count))()
    stat = _get_scaled_samples(ch_index, position, count, data, time)
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    return tuple(time), tuple(data)

# --------------------------------------------------------------------

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

# --------------------------------------------------------------------

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

# --------------------------------------------------------------------

_get_array_info_count = _lib.DWGetArrayInfoCount
_get_array_info_count.argtypes = (ct.c_int,)
_get_array_info_count.restype = ct.c_int
def get_array_info_count(ch_index):
    """Get the number of 'axis' for array channel `ch_index`.

    Can be understood as the number of arrays in the channel
    `ch_index`.

    Return -1 in case of failure.

    ch_index : int
        The channel index.

    Wraps
        int DWGetArrayInfoCount(int ch_index);

    """
    return _get_array_info_count(ch_index)

# --------------------------------------------------------------------
# DWStatus DWGetArrayInfoList(int ch_index, DWArrayInfo* array_inf_list);
# Parameters:
#       ch_index – ch. Identifier
#       array_inf_list – list of DWArrayInfo
# Return value: See above enumerator
# Description: : This function returns the list of array info.

ArrayInfo = namedtuple('ArrayInfo', 'index name unit size')

_get_array_info_list = _lib.DWGetArrayInfoList
_get_array_info_list.argtypes = (ct.c_int, ct.POINTER(dh.DWArrayInfo))
_get_array_info_list.returntype = ct.c_int
def get_array_info_list(ch_index, encoding=None):
    """Return namedtuples with info on each array in `ch_index`.

    ch_index : int
        The channel enumeration.

    encoding : str (or None)
        `locale.getpreferredencoding()` is used if `encding` is None.

    Wraps
        DWStatus DWGetArrayInfoList(int ch_index, DWArrayInfo* array_inf_list);
    """
    infolist = (dh.DWArrayInfo * get_array_info_count(ch_index))()

    stat = _get_array_info_list(ch_index, infolist)
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat).name)
    encoding = encoding or locale.getpreferredencoding()

    return [ArrayInfo(info.index, info.name.decode(encoding),
                      info.unit.decode(encoding), info.size)
            for info in infolist]

# --------------------------------------------------------------------
# DWStatus DWGetArrayIndexValue(int ch_index, int array_info_index, int array_value_index,
# char* value, int value_size);
# Parameters:
#       ch_index – ch. identifier
#       array_info_index – axis identifier
#       array_value_index –index of value on the axis
#       value – value on the axis
#       value_size – maximum size of string value
# Return value: See above enumerator
# Description: This function returns the specific value on the axis.

_get_array_index_value = _lib.DWGetArrayIndexValue
_get_array_index_value.argtypes = (ct.c_int, ct.c_int, ct.c_int, ct.c_char_p,
                                   ct.c_int)
_get_array_index_value.restype = ct.c_int
def get_array_index_value(ch_index, array_info_index, array_value_index,
                          value_size=255, encoding=None):
    """Return the given array info element as a string.

    ch_index : int
        The channel enumeration.

    array_info_index : int
        The array enumeration, (what array).

    array_value_index : int
        The element index of the array.

    value_size : int
        The maximum expected length of the string.

    encoding : str (or None)
        `locale.getpreferredencoding()` is used if `encding` is None.

    Wraps
        DWStatus DWGetArrayIndexValue(int ch_index, int array_info_index,
                                      int array_value_index, char* value,
                                      int value_size);

    """

    textbuffer = ct.create_string_buffer(value_size + 1)
    stat = _get_array_index_value(ch_index, array_info_index,
                                  array_value_index, textbuffer, value_size)
    if stat != 0:
        raise RuntimeError(dh.DWStatus(stat.name))

    return textbuffer.value.decode(encoding or locale.getpreferredencoding())

# --------------------------------------------------------------------


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
        encoding to pass to `get_channel_list()`, which see. Ignored
        (not meaningful) if channel is int.

    Wraps:
        Nothing explicit. This is a support function to simplify getting
        reduced data from a channel.

    """

    index = channel if type(channel) is int else None

    if index is None:
        for ch in get_channel_list(encoding):
            if ch.name == channel:
                index = ch.index
                break
        else:                       # no break
            raise ValueError(channel, 'not found in data')

    cnt, _ = get_reduced_values_count(index)
    return [rec[reduction] for rec in get_reduced_values(index, 0, cnt)]


STORING_TYPE = {
    0: 'ST_ALWAYS_FAST',
    1: 'ST_ALWAYS_SLOW',
    2: 'ST_FAST_ON_TRIGGER',
    3: 'ST_FAST_ON_TRIGGER_SLOW_OTH'
}
