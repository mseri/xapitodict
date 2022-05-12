"""
Library to convert a xapi db xml dump to a python dictionary
"""
from __future__ import print_function, division

import re
import sexpdata
import xmltodict


def load_xml_into_raw_dict(filename):
    """
    Returns a raw dict containing an xml dump
    using `xmltodict.parse`.
    """
    with open(filename) as xapi_dump:
        dump = xmltodict.parse(xapi_dump.read())
        return dump['database']


def unprotect(s):
    """
    Do more or less what
    https://github.com/xapi-project/xen-api/blob/master/ocaml/database/xml_spaces.ml#L89
    does
    """
    if len(s) < 2:
        return s
    buffer = ""
    mapper = {
        "_": "  ",
        ".": " ",
        "t": "\t",
        "n": "\n",
        "r": "\r",
        "%": "%"
    }
    it = zip(s, s[1:] + " ")
    if isinstance(it, list):
        it = iter(it)
    for (l,r) in it:
        if l == "%" and r in mapper:
            buffer += mapper[r]
            try:
                next(it)
            except StopIteration:
                return buffer
        else:
            buffer += l
    return buffer


# pylint: disable=invalid-name
def unsexpify(v):
    """
    This is an helper meant to unsexpify some fields
    of the xapi database.

    Takes a string `v` and tries to run a sexp parser
    on it if it looks meaningful.
    If it looks like a S-expression it returns the
    parsed value, otherwise it returns the string
    stripped of `'`.
    """
    # looks like a sexp expressiona and it's not a copyright notice
    if v.startswith("(") and not v.startswith("(C)"):
        # the sexp parser interprets `'` for quasiquoting,
        # so we need to replace them
        val = v.replace("'", '"')
        # Let's unprotect spaces and other characters
        val = unprotect(val)
        try:
            return sexpdata.loads(val)
        except AssertionError:
            # If it doesn't load as a sexp it probably isn't one.
            pass

    # it's a simple string, remove unnecessary `'`
    val = v.strip("'")
    return unprotect(val)


# pylint: disable=too-many-branches, invalid-name
def weird_dict_to_dict(wd):
    """
    Helper used to get rid of some internal fields,
    normalise the `_` in field names and
    parse the list and dictionaries encoded as
    S-expressions.
    """
    res = {}
    # pylint: disable=invalid-name
    for k, v in wd.items():
        # ignore the internal fields (`_created`, ...)
        if k.startswith("@_"):
            continue

        # remove the `@` added by `xmltodict` and
        # normalize the use of underscores in fields name
        key = k.strip('@').replace("__", "_")

        # parse the sexped lists
        value = unsexpify(v)

        # last booted record is weird and needs attention on its own...
        if key == 'last_booted_record' and 'struct' in value and isinstance(
                value, list):
            value.remove('struct')  # remove the first field, called 'struct'

        # if they are non-empty lists of couples, make them dictionaries
        # this could be the wrong deserialization in rare cases
        if value \
           and isinstance(value, list) \
           and all(len(v) == 2 for v in value):
            value = dict(value)

        # last booted record is really weird...
        if key == 'last_booted_record' and value and isinstance(value, dict):
            new = {}
            # pylint: disable=invalid-name
            for lk, lv in value.items():
                if 'struct' in lv and not isinstance(lv, str):
                    lv.remove('struct')
                    new[lk] = dict(lv)
                elif 'array' in lv:
                    lv.remove('array')
                    new[lk] = lv
                elif 'boolean' in lv:
                    new[lk] = 'false' if lv[1] == '0' else 'true'
                elif 'double' in lv:
                    new[lk] = str(float(lv[1]))
                elif 'dateTime.iso8601' in lv:
                    new[lk] = lv[1]
                elif lk == 'last_booted_record':
                    new[lk] = {}
                else:
                    new[lk] = unprotect(lv)
            value = new

        if key == 'last_booted_record' and not value:
            value = {}

        # associate the parsed values to the polished keys
        res[key] = value

    return res


def polish_raw_blob(obj):
    """
    Take the raw dict import of the xapi db and
    make it into a usable dictionary.

    Return the db dictionary and the version metadata dictionary.
    """

    xapi_db = {}

    # we only care about the database tables for this
    for kind in obj['table']:
        # each kind is a xapi table

        # heuristic parsing of the values imported
        # by `xmltodict` for a xapi database
        name = kind['@name']
        raw_content = kind.get('row', [])
        if raw_content:
            # if the content is parseable by weird_dict_to_dict
            # and not in a list, adapt it first
            if isinstance(raw_content, dict):
                raw_content = [raw_content]

            if not isinstance(raw_content, list):
                # some rows are serialized in a weird way,
                # this is a hack to make the uniform
                content = [raw_content]
            else:
                content = list(map(weird_dict_to_dict, raw_content))

            # add to the xapi table the database rows:
            # a list of dictionaries
            xapi_db[name] = content
        else:
            # deal with empty tables
            xapi_db[name] = []

    # extract version information from the manifest. ['manifest']['pair']
    # looks like this:
    #
    #   [ OrderedDict([('@key', 'schema_major_vsn'), ('@value', '5')])
    #   , OrderedDict([('@key', 'schema_minor_vsn'), ('@value', '109')])
    #   , OrderedDict([('@key', 'generation_count'), ('@value', '941255')])
    #   ]

    version = {}

    for row in obj['manifest']['pair']:
        def if_key_add_it(row, val):
            "Helper for manifest generation"
            if row["@key"] == val:
                version[val] = row["@value"]

        for key in [
                'schema_major_vsn',
                'schema_minor_vsn',
                'generation_count']:
            if_key_add_it(row, key)

    return xapi_db, version


def xapi_to_dict(filename):
    """
    Take the filename of a xapi db dump and
    load it into a usable dictionary.

    Return the db dictionary and the version metadata dictionary.
    """
    obj = load_xml_into_raw_dict(filename)
    return polish_raw_blob(obj)
