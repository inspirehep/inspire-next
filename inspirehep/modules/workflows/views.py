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

from invenio_db import db
from invenio_workflows import workflow_object_class, ObjectStatus
from invenio_workflows.errors import WorkflowsMissingObject

from inspirehep.modules.workflows.models import WorkflowsPendingRecord

blueprint = Blueprint(
    'inspire_workflows',
    __name__,
    url_prefix="/callback",
    template_folder='templates',
    static_folder="static",
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
    try:
        workflow_object = workflow_object_class.get(workflow_id)
    except WorkflowsMissingObject:
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
    db.session.commit()
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
            'success': False,
            'message': 'workflow with id %s not found.' % workflow_id,
        }

    return {
        'success': True,
        'message': 'workflow with id %s continued.' % workflow_id,
    }


def _put_workflow_in_error_state(workflow_id, error_message, result):
    try:
        workflow_object = workflow_object_class.get(workflow_id)
    except WorkflowsMissingObject:
        current_app.logger.error(
            'No workflow object with the id %s could be found.',
            workflow_id,
        )
        return {
            'success': False,
            'message': 'workflow with id %s not found.' % workflow_id,
        }

    workflow_object.status = ObjectStatus.ERROR
    workflow_object.extra_data['callback_result'] = result
    workflow_object.extra_data['_error_msg'] = error_message
    workflow_object.save()
    db.session.commit()

    return {
        'success': True,
        'message': 'workflow %s updated with error.' % workflow_id,
    }


@blueprint.route('/workflows/webcoll', methods=['POST'])
def webcoll_callback():
    """Handle a callback from webcoll with the record ids processed.

    Expects the request data to contain a list of record ids in the
    recids field.

    Example:
        An example of callback::

            $ curl \\
                http://web:5000/callback/workflows/webcoll \\
                -H "Host: localhost:5000" \\
                -F 'recids=1234'


    """
    recids = dict(request.form).get('recids', [])
    pending_records = WorkflowsPendingRecord.query.filter(
        WorkflowsPendingRecord.record_id.in_(recids)
    ).all()
    response = {}
    for pending_record in pending_records:
        recid = int(pending_record.record_id)
        workflow_id = pending_record.workflow_id
        continue_response = _find_and_continue_workflow(
            workflow_id=workflow_id,
            recid=recid,
        )
        if continue_response['success']:
            current_app.logger.debug(
                'Successfully restarted workflow %s',
                workflow_id,
            )
            response[recid] = {
                'success': True,
                'message': 'Successfully restarted workflow %s' % workflow_id,
            }
        else:
            current_app.logger.debug(
                'Error restarting workflow %s: %s',
                workflow_id,
                continue_response['message'],
            )
            response[recid] = {
                'success': False,
                'message': continue_response['message'],
            }

        db.session.delete(pending_record)
        db.session.commit()

    return jsonify(response)


def _robotupload_has_error(result):
    recid = int(result.get('recid'))
    if not result.get('success'):
        message = result.get(
            'error_message',
            'No error message from robotupload.'
        )
    elif recid < 0:
        message = result.get(
            'error_message',
            'Failed to create record on robotupload.',
        )
    else:
        return False, ''

    return True, message


def _parse_robotupload_result(result, workflow_id):
    response = {}
    recid = int(result.get('recid'))

    result_has_error, error_message = _robotupload_has_error(result)
    if result_has_error:
        response = {
            'success': False,
            'message': error_message,
        }
        return response

    already_pending_ones = WorkflowsPendingRecord.query.filter_by(
        record_id=recid,
    ).all()
    if already_pending_ones:
        current_app.logger.warning(
            'The record %s was already found on the pending list.',
            recid
        )
        response = {
            'success': False,
            'message': 'Recid %s already in pending list.' % recid,
        }
        return response

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

    continue_response = _find_and_continue_workflow(
        workflow_id=workflow_id,
        recid=recid,
        result=result,
    )
    if continue_response['success']:
        current_app.logger.debug(
            'Successfully restarted workflow %s',
            workflow_id,
        )
        response = {
            'success': True,
            'message': 'Successfully restarted workflow %s' % workflow_id,
        }
    else:
        current_app.logger.debug(
            'Error restarting workflow %s: %s',
            workflow_id,
            continue_response['message'],
        )
        response = {
            'success': False,
            'message': continue_response['message'],
        }

    return response


@blueprint.route('/workflows/robotupload', methods=['POST'])
def robotupload_callback():
    """Handle callback from robotupload.

    If robotupload was successful caches the workflow
    object id that corresponds to the uploaded record,
    so the workflow can be resumed when webcoll finish
    processing that record.
    If robotupload encountered an error sends an email
    to site administrator informing him about the error.

    Examples:
        An example of failed callback that did not get to create a recid (the
        "nonce" is the workflow id)::

            $ curl \\
                http://web:5000/callback/workflows/robotupload \\
                -H "Host: localhost:5000" \\
                -H "Content-Type: application/json" \\
                -d '{
                    "nonce": 1,
                    "results": [
                        {
                            "recid":-1,
                            "error_message": "Record already exists",
                            "success": false
                        }
                    ]
                }'

        One that created the recid, but failed later::

            $ curl \\
                http://web:5000/callback/workflows/robotupload \\
                -H "Host: localhost:5000" \\
                -H "Content-Type: application/json" \\
                -d '{
                    "nonce": 1,
                    "results": [
                        {
                            "recid":1234,
                            "error_message": "Unable to parse pdf.",
                            "success": false
                        }
                    ]
                }'

        A successful one::

            $ curl \\
                http://web:5000/callback/workflows/robotupload \\
                -H "Host: localhost:5000" \\
                -H "Content-Type: application/json" \\
                -d '{
                    "nonce": 1,
                    "results": [
                        {
                            "recid":1234,
                            "error_message": "",
                            "success": true
                        }
                    ]
                }'
    """

    request_data = request.get_json()
    workflow_id = request_data.get('nonce', '')
    results = request_data.get('results', [])
    responses = {}
    for result in results:
        recid = int(result.get('recid'))

        if recid in responses:
            # this should never happen
            current_app.logger.warning('Received duplicated recid: %s', recid)
            continue

        response = _parse_robotupload_result(
            result=result,
            workflow_id=workflow_id,
        )
        if not response['success']:
            error_set_result = _put_workflow_in_error_state(
                workflow_id=workflow_id,
                error_message='Error in robotupload: %s' % response['message'],
                result=result,
            )
            if not error_set_result['success']:
                response['message'] += (
                    '\nFailed to put the workflow in error state:%s' %
                    error_set_result['message']
                )

        responses[recid] = response

    return jsonify(responses)
