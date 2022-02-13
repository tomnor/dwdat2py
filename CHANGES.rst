Changelog
=========

0.3.2 (2022-02-13)
------------------

- Libraries from Dewesoft updated. Dewesoft changelog say this::

    ## [v4_2_0_21] - 2021-11-29
    FIXED ISSUES:
    -Fix reading file store time in multifile
    -Support reading channels long name
    -DwExportHeader support for DXZ files
    -Fix opening DXZ files

    ## [v4_2_0_20] - 2021-08-02
    FEATURES, IMPROVEMENTS:
    - Improve Matlab example
    - Add mising functions to Linux example
    FIXED ISSUES:
    - Alarms and cursor events not working
    - Fix DWCloseDataFile function

- Update of copyright years.
- Prettify previous change note.


0.3.1 (2021-06-06)
------------------

- Libraries from Dewesoft updated. Dewesoft changelog say this::

    ## [v4_2_0_19] - 2021-06-04
    FIXED ISSUES:
    - DWGetScaledSamplesCount() is zero when using big data file with asynchronous channels


0.3.0 (2021-03-25)
------------------

- Libraries from Dewesoft included with dwdat2py installation.

- README.rst updated about the libs.

- Two new functions to get "scaled" samples, the raw full speed data
  samples, `get_scaled_samples_count()` and `get_scaled_samples()`.
  The latter respects `array_size` (array type of channels).

- A not documented function `get_storing_type()`
  (`DWGetStoringType()`) added with a module level dict `STORING_TYPE`
  to list the meaning of returned value.

- New functions `get_channel_factors`, `get_channel_props.`

- Array related functions `get_array_info_count`, `get_array_info_list`
  and `get_array_index_value` implemented.

- Added repo admin shell script utils/libadmin.sh to simplify commiting
  new version of the libraries. This script is now also responsible for
  the conversion of the doc file to text documentation.


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
