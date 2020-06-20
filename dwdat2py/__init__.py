from . import wrappers

__version__ = '0.1.0'

CONFIGBASENAME = 'dewelibdir'

if os.name == 'nt':
    CONFIGDIR = os.path.expanduser('~')
else:
    CONFIGDIR = os.environ.get('XDG_CONFIG_HOME',
                               os.path.expanduser('~/.config'))
DEWELIBDIR = ''
"""Set this variable to the directory of the dewesoft shared libraries
   if an automated search for the directory is not desired or possible."""


def libdirfind():
    """Return path to dewesoft library directory.

    This function is used by dwdat2py.wrappers.py to find the library
    directory, (unless dwdat2py.DEWELIBDIR variable is set by caller.)

    The path is to be specified by an environment variable DEWELIBDIR or
    a file named dewelibdir (can have extension .txt or .pth), placed in
    ~/.config (or in XDG_CONFIG_HOME if defined) on Gnu/Linux or in ~ on
    Windows. (os.path.expanduser('~') is used).

    With a file, empty lines are ignored and lines starting with # is a
    comment. First non-empty line found is taken as the path to the
    directory with the dewesoft libraries.

    The environment variable is checked first.

    Raise FileNotfounderror or RuntimeError on failure to find the
    library directory.

    """
    libdir = os.getenv('DEWELIBDIR')
    if libdir and os.path.exists(libdir):
        return libdir
    elif libdir:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                libdir)

    if not os.path.exists(CONFIGDIR):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                CONFIGDIR)

    def readpath(fn):
        with open(fn) as fo:    # default encoding
            for line in fo:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                elif stripped:
                    return stripped
            return ''

    configfile = os.path.join(CONFIGDIR, CONFIGBASENAME)
    for ext in ('', '.txt', '.pth'):
        try:
            libdir = readpath(configfile + ext)
            break
        except FileNotFoundError:
            pass

    else:                       # no break
        raise RuntimeError('No configfile found in %s' % CONFIGDIR)

    if libdir and os.path.exists(libdir):
        return libdir
    elif libdir:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT),
                                libdir)

    raise RuntimeError('%s found but no library path in it' % configfile)
