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

"""Callback blueprint for interaction with legacy."""

from __future__ import absolute_import, division, print_function

import re

from os.path import join
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from invenio_db import db
from invenio_workflows import workflow_object_class

from inspirehep.modules.workflows.models import WorkflowsPendingRecord


blueprint = Blueprint(
    'inspire_workflows',
    __name__,
    url_prefix="/callback",
    template_folder='../templates',
    static_folder="../static",
)


def _get_base_url():
    """Return base URL for generated URLs for remote reference."""
    base_url = current_app.config.get(
        "LEGACY_ROBOTUPLOAD_URL",
        current_app.config["SERVER_NAME"],
    )
    if not re.match('^https?://', base_url):
        base_url = 'http://{}'.format(base_url)
    return base_url


def _continue_workflow(workflow_id, recid, result=None):
    """Small wrapper to continue a workflow.

    Will prepare the needed data from the record id and the result data if
    passed.

    :return: True if succeeded, False if the specified workflow id does not
        exist.
    """
    result = result if result is not None else {}
    base_url = _get_base_url()
    workflow_object = workflow_object_class.get(workflow_id)
    if not workflow_object:
        current_app.logger.error(
            'No workflow object with the id %s could be found.',
            workflow_id,
        )
        return False

    workflow_object.extra_data['url'] = join(
        base_url,
        'record',
        str(recid)
    )
    workflow_object.extra_data['recid'] = recid
    workflow_object.extra_data['callback_result'] = result
    workflow_object.save()

    workflow_object.continue_workflow(delayed=True)
    return True


def _find_and_continue_workflow(workflow_id, recid, result=None):
    workflow_found = _continue_workflow(
        workflow_id=workflow_id,
        recid=recid,
        result=result,
    )
    if not workflow_found:
        current_app.logger.warning(
            'The workflow %s was not found.',
            workflow_id,
        )
        return {
            'status': 'failed',
            'message': 'workflow with id %s not found.' % workflow_id,
        }

    return {'status': 'succeeded'}


@blueprint.route('/workflows/webcoll', methods=['POST'])
def webcoll_callback():
    """Handle a callback from webcoll with the record ids processed.

    Expects the request data to contain a list of record ids in the
    recids field.
    """
    recids = dict(request.form).get('recids', [])
    response = {}
    for recid in recids:
        recid = int(recid)
        if recid in response:
            current_app.logger.warning('Received duplicated recid: %s', recid)
            continue

        try:
            pending_record = WorkflowsPendingRecord.query.filter_by(
                record_id=recid,
            ).one()
        except NoResultFound:
            current_app.logger.debug(
                'The record %s was not found on the pending list.',
                recid,
            )
            response[recid] = {
                'status': 'failed',
                'message': 'Recid not in pending list.',
            }
            continue
        except MultipleResultsFound:
            current_app.logger.warning(
                'The record %s is found several times in the pending list.',
                recid,
            )
            response[recid] = {
                'status': 'failed',
                'message': 'Duplicated entries in the pending list.',
            }
            continue

        response[recid] = _find_and_continue_workflow(
            workflow_id=pending_record.workflow_id,
            recid=recid,
        )
        db.session.delete(pending_record)
        db.session.commit()
        if response[recid].get('status') == 'failed':
            continue

    return jsonify(response)


@blueprint.route('/workflows/robotupload', methods=['POST'])
def robotupload_callback():
    """Handle callback from robotupload.

    If robotupload was successful caches the workflow
    object id that corresponds to the uploaded record,
    so the workflow can be resumed when webcoll finish
    processing that record.
    If robotupload encountered an error sends an email
    to site administrator informing him about the error.
    """
    request_data = request.get_json()
    workflow_id = request_data.get('nonce', '')
    results = request_data.get('results', [])
    response = {}
    for result in results:
        recid = int(result.get('recid'))

        if recid in response:
            current_app.logger.warning('Received duplicated recid: %s', recid)
            continue

        already_pending_ones = WorkflowsPendingRecord.query.filter_by(
            record_id=recid,
        ).all()
        if already_pending_ones:
            current_app.logger.warning(
                'The record %s was already found on the pending list.',
                recid
            )
            response[recid] = {
                'status': 'failed',
                'message': 'Recid %s already in pending list.' % recid,
            }
            continue

        pending_entry = WorkflowsPendingRecord(
            workflow_id=workflow_id,
            record_id=recid,
        )
        db.session.add(pending_entry)
        db.session.commit()
        current_app.logger.debug(
            'Successfully added recid:workflow %s:%s to pending list.',
            recid,
            workflow_id,
        )

        response[recid] = _find_and_continue_workflow(
            workflow_id=workflow_id,
            recid=recid,
            result=result,
        )

        if response[recid].get('status') == 'failed':
            continue

        current_app.logger.debug(
            'Successfully restarted workflow %s',
            workflow_id,
        )

    return jsonify(response)
