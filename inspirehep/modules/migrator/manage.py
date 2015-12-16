# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Manage migration from INSPIRE legacy instance."""

from __future__ import print_function

import os
import sys

from flask import current_app
from flask.ext.script import prompt_bool

from invenio_ext.script import Manager
from invenio_ext.sqlalchemy import db

from .tasks import (
    add_citation_counts,
    migrate,
    migrate_broken_records,
)

manager = Manager(usage=__doc__)


@manager.option('--input', '-f', dest='file_input',
                help='Specific collections to migrate.')
@manager.option('--remigrate', '-m', action='store_true', dest='remigrate',
                default=False, help='Try to remigrate broken records')
@manager.option('--broken-output', '-b', dest='broken_output', default=None,
                help='Where to write back records that were not possible to migrate')
@manager.option('--dry-run', '-d', action='store_true', dest='dry_run', default=False,
                help='Whether records should really be imported or not')
def populate(file_input=None,
             remigrate=False,
             broken_output=None,
             dry_run=False):
    """Populates the system with records from migration files.

    Usage: inveniomanage migrator populate -f prodsync20151117173222.xml.gz
        --broken-output=/tmp/broken.xml:
    """
    if remigrate:
        print("Remigrate broken records...")
        migrate_broken_records.delay(broken_output=broken_output, dry_run=dry_run)
    elif file_input and not os.path.isfile(file_input):
        print("{0} is not a file!".format(file_input), file=sys.stderr)
    elif file_input:
        print("Migrating records from file: {0}".format(file_input))

        from invenio_celery.utils import disable_queue, enable_queue
        disable_queue("celery")
        try:
            migrate(os.path.abspath(file_input), broken_output=broken_output,
                    dry_run=dry_run)
        finally:
            enable_queue("celery")


@manager.command
def count_citations():
    add_citation_counts.delay()


@manager.command
def remove_bibxxx():
    """Drop all the legacy bibxxx tables."""
    drop_tables("bib%%x")


@manager.command
def remove_idx():
    """Drop all the legacy BibIndex tables."""
    drop_tables('idx%%')
    drop_tables('tmp_idx%%')


@manager.command
def remove_others():
    """Drop misc legacy tables."""
    drop_tables('aid%%')
    drop_tables('bsk%%')
    drop_tables('rnk%%')
    drop_tables('jrn%%')
    drop_tables('sbm%%')
    drop_tables('swr%%')
    drop_tables('crc%%')


@manager.command
def remove_legacy_tables():
    """Remove all legacy tables."""
    db.session.begin(subtransactions=True)
    try:
        db.engine.execute("SET FOREIGN_KEY_CHECKS=0;")
        remove_others()
        remove_bibxxx()
        remove_idx()
        db.engine.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.session.commit()
    except Exception as err:  # noqa
        db.session.rollback()
        current_app.logger.exception(err)


@manager.command
def clean_records():
    """Truncate all the records from various tables."""
    from sqlalchemy.engine import reflection

    print('>>> Truncating all records.')

    tables_to_truncate = [
        "bibrec",
        "record_json",
    ]
    db.session.begin(subtransactions=True)
    try:
        db.engine.execute("SET FOREIGN_KEY_CHECKS=0;")

        # Grab any table with foreign keys to bibrec for truncating
        inspector = reflection.Inspector.from_engine(db.engine)
        for table_name in inspector.get_table_names():
            for foreign_key in inspector.get_foreign_keys(table_name):
                if foreign_key["referred_table"] == "bibrec":
                    tables_to_truncate.append(table_name)

        if not prompt_bool("Going to truncate: {0}".format(
                "\n".join(tables_to_truncate))):
            return
        for table in tables_to_truncate:
            db.engine.execute("TRUNCATE TABLE {0}".format(table))
            print(">>> Truncated {0}".format(table))

        db.engine.execute("DELETE FROM pidSTORE WHERE pid_type='recid'")
        print(">>> Truncated pidSTORE WHERE pid_type='recid'")

        db.engine.execute("SET FOREIGN_KEY_CHECKS=1;")
        db.session.commit()
    except Exception as err:  # noqa
        db.session.rollback()
        current_app.logger.exception(err)


def drop_tables(table_filter):
    """Drop tables helper."""
    table_names = db.engine.execute(
        "SELECT TABLE_NAME"
        " FROM INFORMATION_SCHEMA.TABLES"
        " WHERE TABLE_NAME LIKE '{0}'"
        " AND table_schema='{1}'".format(
            table_filter,
            current_app.config.get('CFG_DATABASE_NAME')
        )
    ).fetchall()
    for table in table_names:
        db.engine.execute("DROP TABLE {0}".format(table[0]))
        print(">>> Dropped {0}.".format(table[0]))
    print(">>> Removed {0} tables.".format(len(table_names)))


@manager.command
def generate_keywords_list():
    """Generate a list of all possible keywords for the parser."""
    import json
    from .tasks import dotter
    # Get the path of invenio_query_parser.
    import invenio_query_parser as e
    path = e.__file__
    path = path[:-12]
    # Get all the available keywords from inspire config file.
    from invenio_base.globals import cfg
    x = cfg['SEARCH_ELASTIC_KEYWORD_MAPPING']
    keywords = x.keys()
    # Get all the (possible) nested keywords.
    for k in x.values():
        if isinstance(k, dict):
            keywords += k.keys()
    # Get all available keywords from the json schema.
    with open('inspirehep/dojson/hep/schemas/hep-0.0.1.json') as data_file:
        data = json.load(data_file)
        data = data.get('properties')
        res = dotter(data, '', [])
        # Remove unwanted fields from json schema.
        for i in range(len(res)):
            res[i] = res[i][1:]
            res[i] = str(res[i].rsplit('.', 1)[0])
        result = []
        # Remove duplicates.
        for i in res:
            if i not in result:
                result.append(i)
        keywords += result
    # Write the results to a file for invenio_query_parser to read.
    with open(path + "/keywords.py", "w") as fp:
        fp.write('keyword_list = ' + str(keywords))
