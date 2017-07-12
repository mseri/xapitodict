"""
xapi-to-json: simple cli util to dump an xml blob of the xapi db to json
"""
from __future__ import print_function, division

import argparse
import json
import os
import sys

import pkg_resources

import xapitodict


def dump_dict_to_file(filename, db_dict):
    """
    Simple helper to dump an extracted db to json file
    """
    with open(filename, "w") as dump:
        json.dump(db_dict, dump, indent=2)


def dump_dict_to_stdout(db_dict):
    """
    Simple helper to dump an extracted db to json file
    """
    json.dump(db_dict, sys.stdout, indent=2)


def parse_args_or_exit(argv=None):
    """
    Parse command line options
    """
    parser = argparse.ArgumentParser(
        description='CLI util to dump an xml blob of the xapi database to json')
    parser.add_argument('--version', action='version',
                        version="%%(prog)s %s" %
                                pkg_resources.require("xapitodict")[0].version)
    parser.add_argument(
        "-v", "--print-db-version", dest="print_db", action='store_true',
        help="Include the version metadata of the extracted xapi db "
             "in the '_version' key")
    parser.add_argument("xapi_db", metavar="XAPIDB",
                        help="Path to the xml dump of the xapi database")
    parser.add_argument("dest", metavar="DEST",
                        help="Path to the output json file (use - for stdout)")
    return parser.parse_args(argv)


def main(argv=None):
    """
    Entry point
    """

    args = parse_args_or_exit(argv)

    # common failures
    if not os.path.exists(args.xapi_db):
        print("Error: unable to find the database file '{}'".format(args.xapi_db))
        sys.exit(1)
    if os.path.isdir(args.dest):
        print("Error: the output file '{}' already exists and is a folder".format(args.dest))
        sys.exit(1)

    db, vsn = xapitodict.xapi_to_dict(args.xapi_db)
    if args.print_db:
        db["_version"] = vsn

    if args.dest == "-":
        dump_dict_to_stdout(db)
    else:
        dump_dict_to_file(args.dest, db)
        print("'{}' has been converted and saved to '{}'".format(os.path.basename(args.xapi_db),
                                                                 os.path.basename(args.dest)))
