"""
Test the wrappers module.
"""
import sys
import os
import unittest
import gzip
from itertools import zip_longest
from collections import namedtuple

# Testing the local package code but dependencies need to be available on the
# system.
here = os.path.dirname(__file__)
packdir = os.path.abspath(os.path.join(here, os.pardir))
sys.path.insert(0, packdir)

try:
    from dwdat2py import wrappers
except EnvironmentError as e:
    print(e)
    print('tests not possible without the lib, please see README.')
    sys.exit(1)

DATAFILE1 = os.path.join(here, 'Example_Drive01.d7d')
DATAFILE2 = os.path.join(here, 'Test2.dxd')

if not os.path.exists(DATAFILE1):
    with gzip.open(DATAFILE1 + '.gz') as fi, open(DATAFILE1, 'wb') as fo:
        fo.write(fi.read())


# reduced channels
# (time_stamp, ave, min, max, rms)
# keys are time stamp here
DATAFILE1RECORDS_CH0 = {
    0.0: (88.16272020339966, 86.67867183685303,
          89.28495049476624, 88.16669464111328),
    60.5: (82.5995683670044, 82.12530612945557,
           83.04696679115295, 82.59994506835938),
    95.5: (-0.08557390538044274, -0.09765923023223877,
           -0.06714072078466415, 0.0858997106552124)}

DATAFILE2RECORDS_CH1 = {
    0.0: (0.0, 0.0, 0.0, 0.0),
    1.95: (0.0, 0.0, 0.0, 0.0),
    4.4: (0.0, 0.0, 0.0, 0.0)}

Counts = namedtuple('Counts', ('scaled', 'reduced'))

DATAFILE1COUNTS = {
    0: Counts(9580, 192),
    1: Counts(9580, 192),
    3: Counts(9557, 192),
    4: Counts(9557, 192),
    6: Counts(4791, 192),
    8: Counts(4791, 192),
    10: Counts(4791, 192),
    12: Counts(4791, 192),
    14: Counts(479, 192),
    16: Counts(4791, 192),
    17: Counts(4791, 192),
    18: Counts(4791, 192),
    19: Counts(4791, 192),
    21: Counts(4791, 192),
    22: Counts(191, 192),
    23: Counts(191, 192),
    24: Counts(1838, 192),
    25: Counts(1838, 192),
    26: Counts(191, 192),
    27: Counts(9580, 192),
}

DATAFILE1_TIMES_HEADS_TAILS = {
    # Selected channels ([:5], [-5:]) time_stamps of get_scaled_samples()
    0: ((0.0, 0.01, 0.02, 0.03, 0.04), (95.75, 95.76, 95.77, 95.78, 95.79)),
    3: ((0.0, 0.009999999776482582, 0.019999999552965164,
         0.029999999329447746, 0.03999999910593033),
        (95.75, 95.75999999046326, 95.77000001072884,
         95.7800000011921, 95.78999999165535)),
    6: ((0.0, 0.019999999552965164, 0.03999999910593033,
         0.05999999865889549, 0.07999999821186066),
        (95.70999999344349, 95.73000000417233, 95.75,
         95.77000001072884, 95.78999999165535)),
    14: ((0.18000000715255737, 0.3700000047683716, 0.5700000002980232,
          0.7700000107288361, 0.9699999988079071),
         (94.96000000834465, 95.15999999642372, 95.36000001430511,
          95.5599999986589, 95.75999999046326)),
    22: ((0.6400000005960464, 1.1400000005960464, 1.6400000005960464,
          2.1400000005960464, 2.6400000005960464),
         (93.64000000059605, 94.14000000059605, 94.64000000059605,
          95.14000000059605, 95.64000000059605)),
    24: ((0.6800000071525574, 0.7199999988079071, 0.7800000011920929,
          0.8199999928474426, 0.8799999952316284),
         (93.93999999761581, 93.97999998927116, 94.11999999731779,
          94.2800000011921, 94.31999999284744)),
}


class TestWrappersTestfile2(unittest.TestCase):

    def setUp(self):
        self.initresult = wrappers.init()
        if self.initresult != 0:
            self.stop()
        self.dwfileinfo = wrappers.open_data_file(DATAFILE2)

    def test_initresult(self):
        self.assertEqual(self.initresult, 0)

    def test_open_data_file_result(self):
        self.assertTrue(isinstance(self.dwfileinfo, wrappers.FileInfo))

    def test_get_storing_type(self):
        storeint = wrappers.get_storing_type()
        self.assertEqual(storeint, 0)
        self.assertEqual(wrappers.STORING_TYPE[storeint], 'ST_ALWAYS_FAST')

    def test_fileinfo_members(self):
        self.assertEqual(self.dwfileinfo.sample_rate, 20000.0)
        # assertAlmostEqual is also available
        self.assertEqual(self.dwfileinfo.start_store_time, 43998.6823785301)
        self.assertEqual(self.dwfileinfo.duration, 4.441)

    def test_get_version(self):
        version = wrappers.get_version()
        self.assertGreater(version, 0)
        self.assertIsInstance(version, int)

    def test_get_channel_list_count(self):
        self.assertEqual(wrappers.get_channel_list_count(), 2)

    def test_get_channel_list(self):
        channels = wrappers.get_channel_list()
        self.assertEqual(channels[0],
                         wrappers.Channel(index=0, name='Counting', unit='',
                                          description='Rainflow',
                                          color=16711680, array_size=20,
                                          data_type=5))
        self.assertEqual(channels[1],
                         wrappers.Channel(index=1, name='Peak/Valley',
                                          unit='', description='',
                                          color=16711680, array_size=1,
                                          data_type=5))

    def test_get_reduced_values_count(self):
        self.assertEqual(wrappers.get_reduced_values_count(0), (0, 0.05))
        self.assertEqual(wrappers.get_reduced_values_count(1), (89, 0.05))

    def test_get_reduced_values(self):
        # (time_stamp, ave, min, max, rms)
        records = wrappers.get_reduced_values(1, 0, 89)
        recdict = {record[0]: record[1:] for record in records}
        for timestamp, values in DATAFILE2RECORDS_CH1.items():
            for recvalue, should in zip_longest(recdict[timestamp], values):
                self.assertEqual(recvalue, should)

    def test_get_scaled_samples_count(self):
        self.assertEqual(wrappers.get_scaled_samples_count(1), 0)

    def test_get_scaled_samples(self):
        # DATAFILE2 has no normal scaled samples
        pass

    def test_channel_reduced_time_stamps_by_index(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # Channel(index=1, name=b'Peak/Valley', ...
        times = wrappers.channel_reduced(1, 0)
        self.assertEqual(min(times), 0)
        self.assertEqual(max(times), 4.4)
        for previous, current in zip(times, times[1:]):
            self.assertAlmostEqual(current - previous, 0.05)

    def test_channel_reduced_time_stamps_by_name(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # Channel(index=1, name=b'Peak/Valley', ...
        times = wrappers.channel_reduced('Peak/Valley', 0)
        self.assertEqual(min(times), 0)
        self.assertEqual(max(times), 4.4)
        for previous, current in zip(times, times[1:]):
            self.assertAlmostEqual(current - previous, 0.05)

    def test_channel_reduced_ave_by_name(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # Channel(index=1, name=b'Peak/Valley', ...
        averages = wrappers.channel_reduced('Peak/Valley', 1)
        # first and last time_stamp in DATAFILE2RECORDS_CH1 represent
        # the first and last record in channel 0
        self.assertEqual(DATAFILE2RECORDS_CH1[0.0][0], averages[0])
        self.assertEqual(DATAFILE2RECORDS_CH1[4.4][0], averages[-1])

    def test_channel_reduced_ave_by_name_ascii(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # Channel(index=1, name=b'Peak/Valley', ...
        averages = wrappers.channel_reduced('Peak/Valley', 1, encoding='ascii')
        # first and last time_stamp in DATAFILE2RECORDS_CH1 represent
        # the first and last record in channel 0
        self.assertEqual(DATAFILE2RECORDS_CH1[0.0][0], averages[0])
        self.assertEqual(DATAFILE2RECORDS_CH1[4.4][0], averages[-1])

    def tearDown(self):
        result = wrappers.close_data_file()
        if result:
            print('error: close_data_file() returned', result)
        result = wrappers.de_init()
        if result:
            print('error: de_init() returned', result)


class TestWrappersExampleFile01(unittest.TestCase):
    """Test all the functions in wrappers module."""

    def setUp(self):
        self.initresult = wrappers.init()
        if self.initresult != 0:
            self.stop()
        self.dwfileinfo = wrappers.open_data_file(DATAFILE1)

    def test_initresult(self):
        self.assertEqual(self.initresult, 0)

    def test_open_data_file_result(self):
        self.assertTrue(isinstance(self.dwfileinfo, wrappers.FileInfo))

    def test_get_storing_type(self):
        storeint = wrappers.get_storing_type()
        self.assertEqual(storeint, 0)
        self.assertEqual(wrappers.STORING_TYPE[storeint], 'ST_ALWAYS_FAST')

    def test_fileinfo_members(self):
        self.assertEqual(self.dwfileinfo.sample_rate, 100.0)
        # assertAlmostEqual is also available
        self.assertEqual(self.dwfileinfo.start_store_time, 37903.8942918056)
        self.assertEqual(self.dwfileinfo.duration, 95.8)

    def test_get_version(self):
        version = wrappers.get_version()
        self.assertGreater(version, 0)
        self.assertIsInstance(version, int)

    def test_get_channel_list_count(self):
        self.assertEqual(wrappers.get_channel_list_count(), 20)

    def test_get_channel_list(self):
        channels = wrappers.get_channel_list()
        self.assertEqual(channels[0],
                         wrappers.Channel(index=0, name='GPSvel', unit='kph',
                                          description='v', color=16711680,
                                          array_size=1, data_type=2))
        self.assertEqual(channels[-1],
                         wrappers.Channel(index=27, name='CNT 0', unit='m',
                                          description='', color=65280,
                                          array_size=1, data_type=4))

    def test_get_reduced_values_count(self):
        self.assertEqual(wrappers.get_reduced_values_count(0), (192, 0.5))
        self.assertEqual(wrappers.get_reduced_values_count(27), (192, 0.5))

    def test_get_reduced_values(self):
        # (time_stamp, ave, min, max, rms)
        records = wrappers.get_reduced_values(0, 0, 192)
        recdict = {record[0]: record[1:] for record in records}
        for timestamp, values in DATAFILE1RECORDS_CH0.items():
            for recvalue, should in zip_longest(recdict[timestamp], values):
                self.assertEqual(recvalue, should)

    def test_get_scaled_samples_count(self):
        # self.assertEqual(wrappers.get_scaled_samples_count(1), 0)
        chlist = wrappers.get_channel_list()
        for ch in chlist:
            count = wrappers.get_scaled_samples_count(ch.index)
            self.assertEqual(count, DATAFILE1COUNTS[ch.index].scaled)

    def test_get_scaled_samples(self):
        headtails = DATAFILE1_TIMES_HEADS_TAILS
        chlist = wrappers.get_channel_list()
        for ch in chlist:
            if ch.index in headtails:
                count = wrappers.get_scaled_samples_count(ch.index)
                time, data = wrappers.get_scaled_samples(ch.index, 0, count)
                self.assertEqual((time[:5], time[-5:]), headtails[ch.index])

    def test_channel_reduced_time_stamps_by_index(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        times = wrappers.channel_reduced(0, 0)
        self.assertEqual(min(times), 0)
        self.assertEqual(max(times), 95.5)
        for previous, current in zip(times, times[1:]):
            self.assertEqual(current - previous, 0.5)

    def test_channel_reduced_ave_by_index(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        averages = wrappers.channel_reduced(0, 1)
        # first and last time_stamp in DATAFILE1RECORDS_CH0 represent
        # the first and last record in channel 0
        self.assertEqual(DATAFILE1RECORDS_CH0[0.0][0], averages[0])
        self.assertEqual(DATAFILE1RECORDS_CH0[95.5][0], averages[-1])

    def test_channel_reduced_time_stamps_by_name(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        times = wrappers.channel_reduced('GPSvel', 0)
        self.assertEqual(min(times), 0)
        self.assertEqual(max(times), 95.5)
        for previous, current in zip(times, times[1:]):
            self.assertEqual(current - previous, 0.5)

    def test_channel_reduced_ave_by_name(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        averages = wrappers.channel_reduced('GPSvel', 1)
        # first and last time_stamp in DATAFILE1RECORDS_CH0 represent
        # the first and last record in channel 0
        self.assertEqual(DATAFILE1RECORDS_CH0[0.0][0], averages[0])
        self.assertEqual(DATAFILE1RECORDS_CH0[95.5][0], averages[-1])

    def test_channel_reduced_ave_by_name_ascii(self):
        #      0        1    2    3    4
        # (time_stamp, ave, min, max, rms)
        # wrappers.Channel(index=0, name=b'GPSvel', unit=b'kph',
        averages = wrappers.channel_reduced('GPSvel', 1, encoding='ascii')
        # first and last time_stamp in DATAFILE1RECORDS_CH0 represent
        # the first and last record in channel 0
        self.assertEqual(DATAFILE1RECORDS_CH0[0.0][0], averages[0])
        self.assertEqual(DATAFILE1RECORDS_CH0[95.5][0], averages[-1])

    def tearDown(self):
        result = wrappers.close_data_file()
        if result:
            print('error: close_data_file() returned', result)
        result = wrappers.de_init()
        if result:
            print('error: de_init() returned', result)


if __name__ == '__main__':
    unittest.main()
