#! /usr/bin/env python

import sys, os
import unittest
import gzip

here = os.path.dirname(__file__)
packdir = os.path.abspath(os.path.join(here, os.pardir))
sys.path.insert(0, packdir)

DATAFILE = os.path.join(here, 'Example_Drive01.d7d')

class AttrHolder:
    pass

# a global object to hold module attributes (file info, Channel list)
AH = AttrHolder()

class TestWrappers(unittest.TestCase):
    """Test all the functions in wrappers module."""

    def setUp(self):
        """Import the wrappers module and unpack test data."""
        global dw
        from dwdat2py import wrappers as dw

        if not os.path.exists(DATAFILE):
            with gzip.open(DATAFILE + '.gz') as fi, open(DATAFILE, 'wb') as fo:
                fo.write(fi.read())

    # naming of tests is to ensure execution order (name string sort)

    def test01(self):
        """Test that init() return 0"""

        res = dw.init()
        self.assertEqual(res, 0)

    def test02(self):
        """Test open file and tuple (FileInfo) is returned."""
        AH.dw_fi = dw.open_data_file(DATAFILE)
        self.assertTrue(isinstance(AH.dw_fi, dw.FileInfo))

    def test03(self):
        """Attr's of FileInfo is familiar."""

        self.assertTrue(all([hasattr(AH.dw_fi, 'sample_rate'),
                             hasattr(AH.dw_fi, 'start_store_time'),
                             hasattr(AH.dw_fi, 'duration')]))

    def test04(self):
        """Check that version is higher than zero."""
        version = dw.get_version()
        self.assertGreater(version, 0)

    def test05(self):
        """Number of channels is 20."""
        numchannels = dw.get_channel_list_count()
        self.assertEqual(numchannels, 20)

    def test06(self):
        """Get a channel list and it's a list of Channel tuples"""

        AH.channels = dw.get_channel_list()
        self.assertTrue(all([isinstance(ct, dw.Channel) for ct in AH.channels]))

    def test07(self):
        """Attr's of a Channel in the channel list is familiar."""

        channel = AH.channels[0]
        truelist = [hasattr(channel, 'index'), hasattr(channel, 'name'),
                    hasattr(channel, 'unit'), hasattr(channel, 'description'),
                    hasattr(channel, 'color'), hasattr(channel, 'array_size'),
                    hasattr(channel, 'data_type')]

        self.assertTrue(all(truelist))

    def test08(self):
        """Reduced values count and sample time resolution are all the same."""

        countlist = [dw.get_reduced_values_count(ch.index)
                     for ch in AH.channels]

        self.assertTrue(all([cnt == (192, 0.5) for cnt in countlist]))

    def test20(self):
        """Test that close file return 0."""
        res = dw.close_data_file()
        self.assertEqual(res, 0)



if __name__ == '__main__':
    unittest.main()
