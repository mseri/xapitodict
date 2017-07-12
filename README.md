# XAPI to dict (and to json)

`xapitodict` is a library to extract the a xapi db dump into a python
dictionary for ease of analysis and debugging investigation.

If you are more comfortable using other tools (e.g. `jq`) it also provides
an executable, `xapi-to-json` to load the xml database and dump it into
as json into a file or the standard output.  For additional information
run `xapi-to-json --help`.

## Requirements

The packages `sexpdata` and `xmltodict` are required. They are both
available on `pypi` and installable via `pip` or `easy_install`.

## Install

Simply run `python setup.py install` (or `python setup.py install --user`
if you prefer to install it locally).  Make sure that the binary install
path is in your `env` path.
