# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage migrator from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

import os
import re
import csv

import click
import requests

from flask_cli import with_appcontext

from .tasks import (
    add_citation_counts,
    migrate,
    remigrate_records,
    migrate_chunk,
    split_blob,
)
from .models import InspireProdRecords


RE_ERROR_STRING = re.compile(".*: Record \d+: (?P<error>.*)", re.U)


@click.group()
def migrator():
    """Command related to migrating INSPIRE data."""


@migrator.command()
@click.option('--file-input', '-f',
              help='Specific collections to migrate.')
@click.option('--remigrate-broken', '-b', is_flag=True,
              default=False, help='Try to remigrate broken records')
@click.option('--remigrate-all', '-a', is_flag=True,
              default=False, help='Remigrate all records')
@click.option('--wait', '-w', type=bool, default=False,
              help='Wait for migrator to complete.')
def populate(file_input=None,
             remigrate_broken=False,
             remigrate_all=False,
             wait=False):
    """Populates the system with records from migrator files.

    Usage: inveniomanage migrator populate -f prodsync20151117173222.xml.gz
    """
    if remigrate_broken:
        click.echo("Remigrate broken records...")
        remigrate_records.delay(only_broken=True)
    elif remigrate_all:
        click.echo("Remigrate all records...")
        remigrate_records.delay(only_broken=False)
    elif file_input and not os.path.isfile(file_input):
        click.echo("{0} is not a file!".format(file_input), err=True)
    elif file_input:
        click.echo("Migrating records from file: {0}".format(file_input))

        migrate(os.path.abspath(file_input), wait_for_results=wait)


@migrator.command()
@click.option('--recid', '-r', type=int, help="recid on INSPIRE")
def one(recid):
    click.echo(
        "Migrating record {recid} from INSPIRE legacy".format(recid=recid))
    raw_record = requests.get(
        "http://inspirehep.net/record/{recid}/export/xme".format(recid=recid)).content
    migrate_chunk(split_blob(raw_record))


@migrator.command()
def count_citations():
    """Adds field citation_count to every record in 'HEP' and calculates its proper value."""
    click.echo("Adding citation_count to all records")
    add_citation_counts()


@migrator.command()
@click.option('--output', '-o', default="/tmp/broken-records.csv",
              help='Specifiy where to report errors.')
@with_appcontext
def report_errors(output):
    """Reports in a friendly way all failed records and corresponding motivation."""
    click.echo("Reporting broken records into {0}".format(output))
    with open(output, "w") as out:
        csv_writer = csv.writer(out)
        results = InspireProdRecords.query.filter(InspireProdRecords.valid == False) # noqa: ignore=F712
        results_length = results.count()
        with click.progressbar(results.yield_per(100), length=results_length) as bar:
            for obj in bar:
                if 'DELETED' not in obj.marcxml:
                    brief_error = obj.errors.splitlines()[0]
                    g = RE_ERROR_STRING.match(brief_error)
                    if g:
                        csv_writer.writerow((g.group('error'), obj.recid))
