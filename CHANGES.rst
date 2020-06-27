Changelog
=========

0.3.0 (2020-06-xx)
------------------

- Two new functions to get "scaled" samples, the raw full speed data
  samples, `get_scaled_samples_count()` and `get_scaled_samples()`.

- A not documented function `get_storing_type()`
  (`DWGetStoringType()`) added with a module level dict `STORING_TYPE`
  to list the meaning of returned value.

- Tests added for new functions.


0.2.0 (2020-06-21)
------------------

- A config file to specify path to the directory with library files can
  be used, (put in `~/.config` or `~`). `~` derived by
  `os.path.expanduser('~')`.

- Context manager provided for access to the wrappers module,
  `dwdat2py.wrappersimport()`, taking care of init, opening, closing
  data file and de_init.

- Written for Python 3.

- DWDataReaderHeader.py just copied as is to the repo. (instead of
  renaming to dwheader.py and tweaking it).

- Tests rewritten and more tests added.

- Change to Apache 2.0 license.

- DWDataReaderv.doc.txt is produced with

  ``$ antiword DWDataReaderv.doc > DWDataReaderv.doc.txt``

  when the doc file is updated.

0.1.0 (2017-01-01)
------------------

- Make public: Repo created
