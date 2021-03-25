.. -*- coding: utf-8 -*-

dwdat2py
========

DEWESoft, a company making hardware for data acquisition, also provide
software applications (Windows) for working with data sets produced with
the hardware. Files are in their proprietary formats such as .d7d, .d7z
or .dxd. To work with the same data using a programming language like
Python it is necessary to first convert them to a portable format such
as text. To get around this extra step, DEWESoft provide a shared
library called DWDataReaderLib.

dwdat2py is a python package with wrappers around the functions provided
in DWDataReaderLib.

Installation
------------

Using pip
.........

::

   pip install dwdat2py

Installing from source
......................

Clone the repo with ``git clone https://github.com/tomnor/dwdat2py.git``, cd
into dwdat2py directory (the directory with the ``setup.py`` file) and say

::

   pip install .

Libraries are shipped with dwdat2py
...................................

By installation of dwdat2py, the Dewesoft libraries are included. Be
aware that the libraries are gratis but non-free binary blobs. The
libraries come with an EULA that permits use and redistribution in
third party projects as far as I understand it.

Libraries are installed in a sub-directory to dwdat2py called
``libs``.

Libraries are retrieved from
https://download.dewesoft.com/list/developers where one has to
register for an account to get it. Once logged in, find a button
"Dewesoft Data Reader Library", enabling to download a zip file
(DWDataReader.zip) with the libs. Or skip that, since they are
included with dwdat2py.

Usage
-----

.. code:: python

   from dwdat2py import wrappers as dw

   dw.init()
   dw.open_data_file('dat1')
   # ... other functions to get at data in dat1 ...
   dw.close_data_file()
   dw.open_data_file('dat2')
   # ... other functions to get at data in dat2 ...
   dw.close_data_file() # work is done for now
   dw.de_init()
   # optionally init() again for a new session.


The calls ``init()`` and ``de_init()`` must be called first and last
respectively. Make sure ``open_data_file(...)`` is called successfully before
``close_data_file(...)``, else don't call close_data_file.

The highest level function for now in this package is this:

.. code:: python

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

And if you happen to know the index or name of the channels, this function
should suffice to get at the data, channel by channel. Else you would need to
call some helper functions first to prepare for this call.

Access to the wrappers module is also provided as a context manager:

.. code:: python

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

Contribute
----------

Please report bugs and send suggestions or patches to the author. Or
make an issue or pull request on the repo home at `Github
<http://github.com/tomnor/dwdat2py>`_
