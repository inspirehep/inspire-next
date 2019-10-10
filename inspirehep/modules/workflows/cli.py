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

"""CLI for workflows."""

from __future__ import absolute_import, division, print_function

import click

from flask.cli import with_appcontext
from invenio_db import db
from invenio_search import current_search


TABLES = [
    'crawler_workflows_object',
    'workflows_audit_logging',
    'workflows_buckets',
    'workflows_object',
    'workflows_pending_record',
    'workflows_record_sources',
    'workflows_workflow',
]

ES_INDICES = [
    'holdingpen-hep',
    'holdingpen-authors',
]


@click.group()
def workflows():
    """Workflows management command."""
    pass


@workflows.command()
@click.option('--yes-i-know', is_flag=True)
@with_appcontext
def purge(yes_i_know):
    """Removes every entry from DB and ES related to workflows"""
    query = "TRUNCATE {tables} RESTART IDENTITY"
    if not yes_i_know:
        click.confirm(
            'This operation will irreversibly remove data from DB and ES, do you want to continue?',
            abort=True
        )
    click.secho('Truncating tables from DB:\n* {}'.format('\n* '.join(TABLES)))
    db.session.execute(query.format(tables=', '.join(TABLES)))
    db.session.commit()

    click.secho('Removing workflows indices from ES...')
    list(current_search.delete(index_list=ES_INDICES))

    click.secho('Recreating indices...')
    list(current_search.create(ignore_existing=True, index_list=ES_INDICES))

    click.secho('Purge completed')
