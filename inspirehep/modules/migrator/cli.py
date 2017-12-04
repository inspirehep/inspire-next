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

import csv
import os
import sys
import traceback
from itertools import dropwhile

import click
import jsonschema
import requests
from flask_cli import with_appcontext

from dojson.contrib.marc21.utils import create_record

from inspire_dojson import marcxml2record
from inspire_schemas.api import validate
from inspire_utils.helpers import force_list

from .models import InspireProdRecords
from .tasks import (
    add_citation_counts,
    migrate,
    migrate_chunk,
    remigrate_records,
    split_blob,
)

REAL_COLLECTIONS = (
    'INSTITUTION',
    'EXPERIMENT',
    'JOURNALS',
    'JOURNALSNEW',
    'HEPNAMES',
    'JOB',
    'JOBHIDDEN',
    'CONFERENCES',
    'DATA',
)


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
    click.echo('Migrating record {recid} from INSPIRE legacy'.format(recid=recid))
    response = requests.get('http://inspirehep.net/record/{recid}/export/xme'.format(recid=recid))
    response.raise_for_status()
    migrate_chunk(split_blob(response.content))


@migrator.command()
def count_citations():
    """Adds field citation_count to every record in 'HEP' and calculates its proper value."""
    click.echo("Adding citation_count to all records")
    add_citation_counts()


@migrator.command()
@click.option('--output', '-o', default="/tmp/broken-records.csv",
              help='Specifiy where to report errors.')
@with_appcontext
def reporterrors(output):
    """Reports in a friendly way all failed records and corresponding motivation."""
    def get_collection(marc_record):
        collections = set()
        for field in force_list(marc_record.get('980__')):
            for v in field.values():
                for e in force_list(v):
                    collections.add(e.upper().strip())
        if 'DELETED' in collections:
            return 'DELETED'
        for collection in collections:
            if collection in REAL_COLLECTIONS:
                return collection
        return 'HEP'

    click.echo("Reporting broken records into {0}".format(output))
    errors = {}
    results = InspireProdRecords.query.filter(InspireProdRecords.valid == False) # noqa: ignore=F712
    results_length = results.count()
    with click.progressbar(results.yield_per(100), length=results_length) as bar:
        for obj in bar:
            marc_record = create_record(obj.marcxml, keep_singletons=False)
            collection = get_collection(marc_record)
            if 'DELETED' in collection:
                continue
            recid = int(marc_record['001'])
            try:
                json_record = marcxml2record(obj.marcxml)
            except Exception as err:
                tb = u''.join(traceback.format_tb(sys.exc_info()[2]))
                errors.setdefault((collection, 'dojson', tb), []).append(recid)
                continue

            try:
                validate(json_record)
            except jsonschema.exceptions.ValidationError as err:
                exc = [
                    row
                    for row in str(err).splitlines()
                    if row.startswith('Failed validating')
                ][0]
                details = u'\n'.join(
                    dropwhile(
                        lambda x: not x.startswith('On instance'),
                        str(err).splitlines()
                    )
                )
                errors.setdefault(
                    (collection, 'validation', exc), []
                ).append((recid, details))
                continue

    with open(output, "w") as out:
        csv_writer = csv.writer(out)
        for (collection, stage, error), elements in errors.iteritems():
            if stage == 'dojson':
                csv_writer.writerow((
                    collection,
                    stage,
                    error,
                    '\n'.join(
                        'http://inspirehep.net/record/{}'.format(recid)
                        for recid in elements
                    )
                ))
            else:
                for recid, details in elements:
                    csv_writer.writerow((
                        collection,
                        stage,
                        error,
                        'http://inspirehep.net/record/{}'.format(recid),
                        details
                    ))
    click.echo("Dumped errors into {}".format(output))
