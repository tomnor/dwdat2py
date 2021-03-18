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


import os
import errno
from contextlib import contextmanager

__version__ = '0.3.0'

DEWELIBDIR = ''
"""Set this variable to the directory of the dewesoft shared libraries
   to use other versions of the libs than those provided."""


def libdirfind():
    """Return path to dewesoft library directory.

    It is the path to the provided library blobs if DEWELIBDIR
    module variable is the empty string.

    Raise FileNotFoundError or RuntimeError on failure to find the
    library directory.

    """
    libdir = DEWELIBDIR
    if libdir and os.path.exists(libdir):
        return libdir
    elif libdir:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                libdir)

    thisdir = os.path.abspath(os.path.dirname(__file__))
    libdir = os.path.join(thisdir, 'libs')
    if libdir and os.path.exists(libdir):
        return libdir
    elif libdir:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                libdir)


@contextmanager
def wrappersimport(fn, fsencoding=None):
    """Provide context access to the wrappers module.

    Return a handle to the wrappers module in a context manager and file
    `fn` (str) opened for operations (a .dxd file for example).
    Initialization and deinitialization is provided by this context
    manager, as well as opening and closing the file.

    The file information resulting from opening the file is available as
    a module level variable `fileinfo`, (`handle.fileinfo`).

    The function that `wrappers.open_data_file` wraps require bytes as
    file name. `fsencoding` is used in the call to
    `wrappers.open_data_file` but is hopefully not necessary to specify
    since os.fsencode() is used by default.

    Example usage:

    >>> import dwdat2py
    >>> with dwdat2py.wrappersimport(fn) as wi:
    ...    print(wi.fileinfo)
    ...    chlist = wi.get_channel_list(encoding='latin1')
    ...    for chinfo in chlist:
    ...        # print the average values from each channel (1)
    ...        print(wi.channel_reduced(chinfo.index, 1))
    ...    # get the "time stamps" (0)
    ...    time = wi.channel_reduced(chlist[0].index, 0)

    As with importing the wrappers module in the standard way, this will
    fail if the shared library is not found.

    """

    from . import wrappers
    wrappers.init()
    init = True
    fileinfo = wrappers.open_data_file(fn, fsencoding)
    opened = True
    wrappers.fileinfo = fileinfo
    try:
        yield wrappers
    finally:
        if opened:
            wrappers.close_data_file()
        if init:
            wrappers.de_init()
