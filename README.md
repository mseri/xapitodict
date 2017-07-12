# XAPI to dict (and to json)

`xapitodict` is a library to extract the a xapi db dump into a python
dictionary for ease of analysis and debugging investigation.

### CLI

If you are more comfortable using other tools (e.g. `jq`) it also provides
an executable, `xapi-to-json` to load the xml database and dump it into
as json into a file or the standard output.  For additional information
run `xapi-to-json --help`.

### Python Module

If you `import xapitodict` in your `python` (or `jupyter`) session, you have
access to the following function:

```xapi_to_dict: xml_database_path -> (xapi_db_dict, xapi_db_version_dict)```

This takes the path of a xml xapi db dump and returns the database
dictionary and the version metadata dictionary.

## Requirements

The library is compatible with `python 2.7` and `python 3`.

The packages `sexpdata` and `xmltodict` are required. They are both
available on `pypi` and installable via `pip` or `easy_install`.

## Install

Simply run `python setup.py install` (or `python setup.py install --user`
if you prefer to install it locally).  Make sure that the binary install
path is in your `env` path.
