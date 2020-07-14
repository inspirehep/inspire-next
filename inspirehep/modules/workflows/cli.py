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
import datetime
from sqlalchemy import or_

from flask.cli import with_appcontext
from invenio_db import db
from invenio_search import current_search
from invenio_workflows import workflow_object_class, ObjectStatus
from invenio_workflows.models import WorkflowObjectModel


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


@workflows.command()
@click.argument(
    'error_message',
    type=str,
    metavar='<partial_error_message>'
)
@click.option(
    '--from-beginning',
    is_flag=True,
    help="Use this option to restart the workflows from the first step."
)
@with_appcontext
def restart_by_error(error_message, from_beginning):
    """Restart all the workflows in ERROR matching the given error message."""
    errors = WorkflowObjectModel.query.filter_by(status=ObjectStatus.ERROR).all()
    to_restart = [e.id for e in errors if error_message in e.extra_data['_error_msg']]

    click.secho("Found {} workflows to restart from {}".format(
        len(to_restart),
        "first step" if from_beginning else "current step"
    ))

    for wf_id in to_restart:
        obj = workflow_object_class.get(wf_id)
        if from_beginning:
            obj.callback_pos = [0]
            obj.status = ObjectStatus.INITIAL
        else:
            obj.status = ObjectStatus.RUNNING
        obj.save()
        db.session.commit()
        obj.continue_workflow('restart_task', True)
        click.secho("Workflow {} restarted successfully".format(wf_id))


@workflows.command(help="Deletes edit_article workflows in WAITING state older than the number of hours given.")
@click.option(
    "--hours",
    "-h",
    help="Number of hours",
    type=int,
    default=48,
    show_default=True,
)
@with_appcontext
def delete_edit_article_older_than(hours):
    max_date = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)

    waiting = WorkflowObjectModel.query.filter_by(status=ObjectStatus.WAITING)\
        .filter(or_(WorkflowObjectModel.created <= max_date,
                    WorkflowObjectModel.created == None  # noqa: E711
                    ))\
        .filter(WorkflowObjectModel.workflow.has(name="edit_article"))\
        .all()

    click.secho("Found {} workflows to delete older than {} hours".format(
        len(waiting),
        hours
    ))
    for wf in waiting:
        wf = workflow_object_class.get(wf.id)
        wf.delete()
        db.session.commit()
        click.secho("Workflow {} deleted successfully".format(wf.id))
