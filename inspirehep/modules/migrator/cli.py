# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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


"""Manage migrator from INSPIRE legacy instance."""

from __future__ import print_function


import click
import json
import os
import sys

from flask import current_app
from flask.ext.script import prompt_bool
from flask_cli import with_appcontext

from invenio_db import db

from .tasks.records import (
    add_citation_counts,
    migrate,
    migrate_broken_records,
)

from .tasks.remoteaccount import load_remoteacount


@click.group()
def migrator():
    """Command related to migrating INSPIRE data."""


@migrator.command()
@click.option('--file-input', '-f',
              help='Specific collections to migrate.')
@click.option('--remigrate', '-m', type=bool,
              default=False, help='Try to remigrate broken records')
@click.option('--broken-output', '-b',
              help='Where to write back records that were not possible to migrate')
@click.option('--dry-run', '-d', type=bool, default=False,
              help='Whether records should really be imported or not')
@click.option('--wait', '-w', type=bool, default=False,
              help='Wait for migrator to complete.')
def populate(file_input=None,
             remigrate=False,
             broken_output=None,
             dry_run=False,
             wait=False):
    """Populates the system with records from migrator files.

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

        migrate(os.path.abspath(file_input), broken_output=broken_output,
                dry_run=dry_run, wait_for_results=wait)


@migrator.command()
def count_citations():
    """Adds field citation_count to every record in 'HEP' and calculates its proper value."""
    print("Adding citation_count to all records")
    add_citation_counts()


@migrator.command()
@click.argument('source', type=click.File('r'), default=sys.stdin)
@with_appcontext
def loadremoteaccount(source):
    """Load legacy workflow objects into Holding Pen."""
    click.echo('Loading dump...')
    data = json.load(source)

    click.echo('Sending tasks to queue...')
    with click.progressbar(data) as records:
        for item in records:
            load_remoteacount.delay(item)


@migrator.command()
def remove_bibxxx():
    """Drop all the legacy bibxxx tables."""
    drop_tables("bib%%x")


@migrator.command()
def remove_idx():
    """Drop all the legacy BibIndex tables."""
    drop_tables('idx%%')
    drop_tables('tmp_idx%%')


@migrator.command()
def remove_others():
    """Drop misc legacy tables."""
    drop_tables('aid%%')
    drop_tables('bsk%%')
    drop_tables('rnk%%')
    drop_tables('jrn%%')
    drop_tables('sbm%%')
    drop_tables('swr%%')
    drop_tables('crc%%')


@migrator.command()
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


@migrator.command()
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
