# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage migration from INSPIRE legacy instance."""

from __future__ import print_function

import os
import sys

from flask import current_app

from invenio.ext.script import Manager

from .tasks import migrate

manager = Manager(description=__doc__)


@manager.option('--records', '-r', dest='records',
                action='append',
                default=None,
                help='Specific record IDs to migrate.')
@manager.option('--collection', '-c', dest='collections',
                action='append',
                default=None,
                help='Specific collections to migrate.')
@manager.option('--input', '-f', dest='file_input',
                help='Specific collections to migrate.')
def populate(records, collections, file_input=None):
    """Train a set of records from the command line.

    Usage: inveniomanage predicter train -r /path/to/json -o model.pickle
    """
    if records is None and collections is None:
        # We harvest all
        print("Migrating all records...", file=sys.stderr)
    if records:
        print("Migrating records: {0}".format(",".join(records)))
    if collections:
        print("Migrating collections: {0}".format(",".join(collections)))

    if file_input and not os.path.isfile(file_input):
        print("{0} is not a file!".format(file_input), file=sys.stderr)
        return

    legacy_base_url = current_app.config.get("CFG_INSPIRE_LEGACY_BASEURL")
    print("Migrating records from {0}".format(legacy_base_url), file=sys.stderr)

    job = migrate.delay(legacy_base_url,
                        records=records,
                        collections=collections,
                        file_input=file_input)
    print("Scheduled job {0}".format(job.id))


@manager.command
def remove_bibxxx():
    """Drop all the legacy bibxxx tables."""
    from invenio.ext.sqlalchemy import db
    table_names = db.engine.execute(
        "SELECT TABLE_NAME"
        " FROM INFORMATION_SCHEMA.TABLES"
        " WHERE ENGINE='MyISAM'"
        " AND TABLE_NAME LIKE '%%_bib%%x'"
        " AND table_schema='{0}'".format(
            current_app.config.get('CFG_DATABASE_NAME')
        )
    ).fetchall()
    for table in table_names:
        db.engine.execute("DROP TABLE {0}".format(table[0]))
        print(">>> Dropped {0}.".format(table[0]))
    print(">>> Removed {0} tables.".format(len(table_names)))


@manager.command
def remove_idx():
    """Deop all the legacy BibIndex tables."""
    from invenio.ext.sqlalchemy import db
    table_names = db.engine.execute(
        "SELECT TABLE_NAME"
        " FROM INFORMATION_SCHEMA.TABLES"
        " WHERE ENGINE='MyISAM'"
        " AND TABLE_NAME LIKE 'idx%%'"
        " AND table_schema='{0}'".format(
            current_app.config.get('CFG_DATABASE_NAME')
        )
    ).fetchall()
    for table in table_names:
        db.engine.execute("DROP TABLE {0}".format(table[0]))
        print(">>> Dropped {0}.".format(table[0]))
    print(">>> Removed {0} tables.".format(len(table_names)))


@manager.command
def clean_records():
    """Truncate all the record tables."""
    print('>>> Truncating all records.')
