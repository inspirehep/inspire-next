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

import logging
import os

import click
import requests
from flask_sqlalchemy import models_committed

from inspirehep.modules.records.receivers import receive_after_model_commit

from .tasks.records import (
    add_citation_counts,
    migrate,
    migrate_broken_records,
    migrate_chunk,
    split_blob,
)


@click.group()
def migrator():
    """Command related to migrating INSPIRE data."""
    logging.basicConfig()
    # Disable auto-indexing receiver in migration tasks
    models_committed.disconnect(receive_after_model_commit)


@migrator.resultcallback()
def process_result(result, **kwargs):
    """Callback run after migrator commands."""
    models_committed.connect(receive_after_model_commit)


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
