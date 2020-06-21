from setuptools import setup
import re


def version():
    with open('dwdat2py/__init__.py') as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def pkg_readme():
    with open('README.rst') as fo:
        return fo.read()


setup(name='dwdat2py',
      version=version(),
      description='Python wrappers around functions in Dewesoft DWDataReaderLib shared library',
      long_description=pkg_readme(),
      author='Tomas Nordin',
      author_email='tomasn@posteo.net',
      url='https://github.com/tomnor/dwdat2py',
      download_url='https://github.com/tomnor/dwdat/tarball/master',
      license='Apache 2.0',
      packages=['dwdat2py'],
      classifiers=[
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: Apache Software License",
          "Topic :: Scientific/Engineering :: Information Analysis",
          "Topic :: Scientific/Engineering :: Visualization",
          "Programming Language :: Python :: 3",
          "Operating System :: POSIX :: Linux",
          "Operating System :: Microsoft :: Windows",
          "Development Status :: 3 - Alpha"
      ])
