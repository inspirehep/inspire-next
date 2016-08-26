# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage migrator from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

import logging
import os
import sys

import click
from flask import current_app
from flask_cli import with_appcontext

from invenio_db import db

from .tasks import (
    add_citation_counts,
    migrate,
    migrate_broken_records,
)


@click.group()
def migrator():
    """Command related to migrating INSPIRE data."""
    logging.basicConfig()


@migrator.command()
@click.option('--file-input', '-f',
              help='Specific collections to migrate.')
@click.option('--remigrate', '-m', type=bool,
              default=False, help='Try to remigrate broken records')
@click.option('--wait', '-w', type=bool, default=False,
              help='Wait for migrator to complete.')
def populate(file_input=None,
             remigrate=False,
             wait=False):
    """Populates the system with records from migrator files.

    Usage: inveniomanage migrator populate -f prodsync20151117173222.xml.gz
    """
    if remigrate:
        click.echo("Remigrate broken records...")
        migrate_broken_records.delay()
    elif file_input and not os.path.isfile(file_input):
        click.echo("{0} is not a file!".format(file_input), err=True)
    elif file_input:
        click.echo("Migrating records from file: {0}".format(file_input))

        migrate(os.path.abspath(file_input), wait_for_results=wait)


@migrator.command()
def count_citations():
    """Adds field citation_count to every record in 'HEP' and calculates its proper value."""
    click.echo("Adding citation_count to all records")
    add_citation_counts()


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
@with_appcontext
def clean_records():
    """Truncate all the records from various tables."""
    from sqlalchemy.engine import reflection
    from invenio_search import current_search

    click.secho('>>> Truncating all records.')

    tables_to_truncate = [
        "records_metadata",
        "records_metadata_version",
        "inspire_prod_records",
        "inspire_orcid_records",
        "pidstore_pid",
    ]
    db.session.begin(subtransactions=True)
    try:
        # Grab any table with foreign keys to records_metadata for truncating
        inspector = reflection.Inspector.from_engine(db.engine)
        for table_name in inspector.get_table_names():
            for foreign_key in inspector.get_foreign_keys(table_name):
                if foreign_key["referred_table"] == "records_metadata":
                    tables_to_truncate.append(table_name)

        if not click.confirm("Going to truncate:\n{0}".format(
                "\n".join(tables_to_truncate))):
            return

        click.secho('Truncating tables...', fg='red', bold=True,
                    err=True)
        with click.progressbar(tables_to_truncate) as tables:
            for table in tables:
                db.engine.execute("TRUNCATE TABLE {0} RESTART IDENTITY CASCADE".format(table))
                click.secho("\tTruncated {0}".format(table))

        db.session.commit()

        current_search.aliases = {
            k: v for k, v in current_search.aliases.iteritems()
            if k.startswith('records')
        }
        click.secho('Destroying indexes...',
                    fg='red',
                    bold=True,
                    err=True)
        with click.progressbar(
                current_search.delete(ignore=[400, 404])) as bar:
            for name, response in bar:
                click.secho(name)

        click.secho('Creating indexes...',
                    fg='green',
                    bold=True,
                    err=True)
        with click.progressbar(
                current_search.create(ignore=[400])) as bar:
            for name, response in bar:
                click.secho(name)

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
        click.echo(">>> Dropped {0}.".format(table[0]))
    click.echo(">>> Removed {0} tables.".format(len(table_names)))
