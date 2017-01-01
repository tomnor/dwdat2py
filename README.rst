.. -*- coding: utf-8 -*-


**Work in progress, the setup script is not ready and tested**

**Package not on pypi yet**

**Can be used for experiments**

dwdat2py
========

DEWESoft, a company making hardware for data acquisition provide software
applications (Windows) for working with data sets with their proprietary formats
such as .d7d, .d7z or .dxd, the formats data is saved to. To work with the same
data using a programming language like python it is necessary to first convert
to a portable format such as text. To get around this extra step, DEWESoft
provide a shared library called DWDataReaderLib.

dwdat2py is a python package with wrappers around the functions provided in
DWDataReaderLib.

Installation
------------

Using pip
.........

::

   pip install dwdat2py

Installing from source
......................

Download the source from <the github repo>, cd into the dwdat2py src directory
(the directory with the ``setup.py`` file) and say

::

   python setup.py install

or do

::

   pip install .

Get the library file(s) and prepare for use
...........................................

DEWESoft choose to provide the library with a non-free license and it is not
provided with dwdat2py. It can be obtained gratis at
http://www.dewesoft.com/developers, but one need to register for an account. The
archive is called ``DWDataReader_v4_2_0_1.zip`` at writing. A later or earlier
version should work as well, else please report it.

Unpack that archive and put the library files for your system into a directory
of choice, probably on the machine you work on. There is only one file needed,
for example the ``DWDataReaderLib64.so`` or the ``DWDataReaderLib64.dll``, but
it's ok to just dump them all into a directory and let dwdat2py select the right
one at import time.

Finally, set an environment variable ``DEWELIBDIR`` to the directory where the
lib file(s) are put. That's it.

There is a "competing" package called dwdatareader_ which provide the library
files with its distribution, so alternatively get the lib files from there or
try that package out as well [1]_.

.. _dwdatareader: https://github.com/costerwi/dwdatareader

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

  
    def channel_reduced(channel, reduction):
        """Return a list of data for channel reduced to reduction.

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

And if you happen to know the index or name of the channels, this function
should suffice to get at the data, channel by channel. Else you would need to
call some helper functions first to prepare for this call.

Contribute
----------

Please report bugs and send suggestions or patches to the author. Or make an
issue or pull request on the repo home at `Github <http://github.com/tomnor/dwdat>`_

.. [1] dwdatareader solves the same problem but with higher level of abstraction
       to the library functions.
