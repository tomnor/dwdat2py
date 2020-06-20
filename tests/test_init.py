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


if __name__ == '__main__':
    unittest.main()
