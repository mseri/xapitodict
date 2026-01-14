"""
xapi-to-sql: simple cli util to dump an xml blob of the xapi db to SQL
"""
from __future__ import print_function, division

import argparse
from sqlite_utils import Database
import os
import sys

from importlib.metadata import version, PackageNotFoundError

import xapitodict

try:
    __version__ = version("xapitodict")
except PackageNotFoundError:
    # package is not installed
    pass

def dump_to_db(db: Database, db_dict: dict) -> None:
    for tablename, table in db_dict.items():
        db[tablename].insert_all(table, pk = "ref", strict=True)

def dump_dict_to_file(filename, db_dict: dict):
    """
    Simple helper to dump an extracted db to json file
    """
    db = Database(filename)
    dump_to_db(db, db_dict)
    db.close()


def dump_dict_to_stdout(db_dict):
    """
    Simple helper to dump an extracted db to json file
    """
    db = Database(memory=True)
    dump_to_db(db, db_dict)
    for line in db.iterdump():
        print(line)
    db.close()


def parse_args_or_exit(argv=None):
    """
    Parse command line options
    """
    parser = argparse.ArgumentParser(
        description='CLI util to dump an xml dump of the xapi db to json')
    parser.add_argument('--version', action='version',
                        version="%%(prog)s %s" % __version__)
    parser.add_argument(
        "-v", "--print-db-version", dest="print_db", action='store_true',
        help="Include the version metadata of the extracted xapi db "
             "in the '_version' key")
    parser.add_argument("xapi_db", metavar="XAPIDB",
                        help="Path to the xml dump of the xapi database")
    parser.add_argument("-o", "--output", metavar="DEST",
                        dest="dest", default=None,
                        help="Path to the output SQLite file. "
                             "Print to stdout when missing")
    return parser.parse_args(argv)


def main(argv=None):
    """
    Entry point
    """

    args = parse_args_or_exit(argv)

    # common failures
    if not os.path.exists(args.xapi_db):
        sys.exit("Error: unable to find the database file '{}'".
                 format(args.xapi_db))

    if args.dest is not None and os.path.isdir(args.dest):
        sys.exit("Error: the output file '{}' already exists and is a folder".
                 format(args.dest))

    # pylint: disable=invalid-name
    db, vsn = xapitodict.xapi_to_dict(args.xapi_db)
    if args.print_db:
        db["_version"] = vsn

    if args.dest is not None:
        dump_dict_to_file(args.dest, db)
        print("'{}' has been converted and saved to '{}'".format(
            os.path.basename(args.xapi_db),
            os.path.basename(args.dest)), file=sys.stderr)
    else:
        dump_dict_to_stdout(db)
