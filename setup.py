#!/usr/bin/env python

from distutils.core import setup

# Read module version from init file
with open('dwdat/__init__.py') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line)

setup(name='dwdat',
      version=__version__,
      description='Python wrappers around functions in Dewesoft DWDataReaderLib shared library',
      long_description=open('README.rst').read(),
      author='Tomas Nordin',
      author_email='tomasn@posteo.net',
      url='https://github.com/tomnor/dwdat/',
      download_url='https://github.com/tomnor/dwdat/tarball/master',
      license='MIT',
      packages=['dwdat'],
      # package_data={'dwdatareader': ['DW*.dll', 'DW*.so']},
      requires=[
          'enum34',
      ],
      classifiers = [
          "Intended Audience :: Science/Research",
          "Topic :: Scientific/Engineering :: Information Analysis",
          "Topic :: Scientific/Engineering :: Visualization"
          "Programming Language :: Python :: 2.7",
          # "Programming Language :: Python :: 3",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX :: Linux",
          "Development Status :: 2 - Pre-Alpha",
      ],
  )
