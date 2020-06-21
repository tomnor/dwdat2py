"""
Test the __init__ module.
"""
import os
import sys
import unittest
import tempfile
import importlib

# Testing the local package
here = os.path.dirname(__file__)
packdir = os.path.abspath(os.path.join(here, os.pardir))
sys.path.insert(0, packdir)

import dwdat2py

DATAFILE1 = os.path.join(here, 'Example_Drive01.d7d')

if not os.path.exists(DATAFILE1):
    with gzip.open(DATAFILE1 + '.gz') as fi, open(DATAFILE1, 'wb') as fo:
        fo.write(fi.read())

# (time_stamp, ave, min, max, rms)
# keys are time stamp here
DATAFILE1RECORDS_CH0 = {
    0.0: (88.16272020339966, 86.67867183685303,
          89.28495049476624, 88.16669464111328),
    60.5: (82.5995683670044, 82.12530612945557,
           83.04696679115295, 82.59994506835938),
    95.5: (-0.08557390538044274, -0.09765923023223877,
           -0.06714072078466415, 0.0858997106552124)}


class Testlibdirfind_Environ(unittest.TestCase):
    """Test libdirfind function with environment variable available."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        os.environ['DEWELIBDIR'] = self.tempdir

    def test_direxists(self):
        self.assertTrue(os.path.exists(dwdat2py.libdirfind()))

    def test_pathequal(self):
        self.assertEqual(dwdat2py.libdirfind(), self.tempdir)

    def test_nonexistent_libdir(self):
        os.environ['DEWELIBDIR'] = '/this/dir/does/not/exist'
        self.assertRaises(FileNotFoundError, dwdat2py.libdirfind)

    def tearDown(self):
        os.rmdir(self.tempdir)


class Testlibdirfind_configfile(unittest.TestCase):
    """Test libdirfind function with a config file."""

    def setUp(self):
        # we are mocking variables in dwdat2py.__init__, so reload it
        importlib.reload(dwdat2py)

        # make temporary file in derived configdir
        self.tempfd, self.tempfile = tempfile.mkstemp(dir=dwdat2py.CONFIGDIR)
        self.tempdir = tempfile.mkdtemp()  # fake libdir

        # config file including comments and empty lines (besides the
        # path to fake libdir)
        self.fo = os.fdopen(self.tempfd, 'w+')
        self.fo.write('\n# this is a comment\n\n')
        self.fo.write(self.tempdir + 4 * '\n')
        self.fo.flush()

        # mock the CONFIGBASENAME
        dwdat2py.CONFIGBASENAME = os.path.basename(self.tempfile)
        # mock out possible environ variable
        os.environ.pop('DEWELIBDIR', None)

        # fake configdir that is empty
        self.emptyconfigdir = tempfile.mkdtemp()

    def test_libdirpath_ok(self):
        self.assertEqual(dwdat2py.libdirfind(), self.tempdir)

    def test_libdirpath_nok(self):
        self.fo.seek(0)
        self.fo.write('/this/dir/does/not/exist\n')
        self.fo.flush()
        self.assertRaises(FileNotFoundError, dwdat2py.libdirfind)

    def test_configfile_not_found(self):
        dwdat2py.CONFIGDIR = self.emptyconfigdir
        self.assertRaises(RuntimeError, dwdat2py.libdirfind)

    def test_no_path_in_configfile(self):
        self.fo.seek(0)
        self.fo.truncate(0)
        self.fo.flush()
        self.assertRaises(RuntimeError, dwdat2py.libdirfind)

    def test_configdir_not_found(self):
        dwdat2py.CONFIGDIR = '/this/dir/does/not/exist'
        self.assertRaises(FileNotFoundError, dwdat2py.libdirfind)

    def tearDown(self):
        self.fo.close()
        os.remove(self.tempfile)
        os.rmdir(self.tempdir)
        os.rmdir(self.emptyconfigdir)


class TestWrappersImport(unittest.TestCase):

    def test_fileinfo(self):
        with dwdat2py.wrappersimport(DATAFILE1) as wi:
            self.assertEqual(wi.fileinfo.sample_rate, 100.0)
            # assertAlmostEqual is also available
            self.assertEqual(wi.fileinfo.start_store_time, 37903.8942918056)
            self.assertEqual(wi.fileinfo.duration, 95.8)

    def test_get_channel_list_count(self):

        with dwdat2py.wrappersimport(DATAFILE1) as wi:
            self.assertEqual(wi.get_channel_list_count(), 20)

    def test_get_channel_list(self):
        with dwdat2py.wrappersimport(DATAFILE1) as wi:
            channels = wi.get_channel_list()
            self.assertEqual(channels[0],
                             wi.Channel(index=0, name='GPSvel', unit='kph',
                                        description='v', color=16711680,
                                        array_size=1, data_type=2))
            self.assertEqual(channels[-1],
                             wi.Channel(index=27, name='CNT 0', unit='m',
                                        description='', color=65280,
                                        array_size=1, data_type=4))

    def test_channel_reduced_ave_by_index(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        with dwdat2py.wrappersimport(DATAFILE1) as wi:
            averages = wi.channel_reduced(0, 1)
            # first and last time_stamp in DATAFILE1RECORDS_CH0 represent
            # the first and last record in channel 0
            self.assertEqual(DATAFILE1RECORDS_CH0[0.0][0], averages[0])
            self.assertEqual(DATAFILE1RECORDS_CH0[95.5][0], averages[-1])

    def test_channel_reduced_time_stamps_by_name(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        with dwdat2py.wrappersimport(DATAFILE1) as wi:
            times = wi.channel_reduced('GPSvel', 0)
            self.assertEqual(min(times), 0)
            self.assertEqual(max(times), 95.5)
            for previous, current in zip(times, times[1:]):
                self.assertEqual(current - previous, 0.5)

    def test_channel_reduced_ave_by_name(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',

        with dwdat2py.wrappersimport(DATAFILE1) as wi:
            averages = wi.channel_reduced('GPSvel', 1)
            # first and last time_stamp in DATAFILE1RECORDS_CH0 represent
            # the first and last record in channel 0
            self.assertEqual(DATAFILE1RECORDS_CH0[0.0][0], averages[0])
            self.assertEqual(DATAFILE1RECORDS_CH0[95.5][0], averages[-1])


if __name__ == '__main__':
    unittest.main()
