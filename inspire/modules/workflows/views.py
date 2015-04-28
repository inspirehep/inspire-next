# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from os.path import join
from flask import Blueprint, jsonify, request

from invenio.ext.cache import cache
from invenio.base.globals import cfg
from invenio.modules.workflows.models import BibWorkflowObject


blueprint = Blueprint(
    'inspire_workflows',
    __name__,
    url_prefix="/callback",
    template_folder='templates',
    static_folder="static",
)


@blueprint.route('/workflows/continue', methods=['POST'])
def continue_workflow_callback():
    """Handle callback to continue a workflow.

    Expects the request data to contain a object ID in the
    nonce field.
    """
    request_data = request.get_json()
    id_object = request_data.get("nonce", "")

    if id_object:
        callback_results = request_data.get("results", {})
        workflow_object = BibWorkflowObject.query.get(id_object)
        if workflow_object:
            results = request_data.get("results", [])
            for result in results:
                status = result.get('success', False)
                if status:
                    recid = result.get('recid')
                    extra_data = workflow_object.get_extra_data()
                    extra_data['url'] = join(
                        cfg["CFG_ROBOTUPLOAD_SUBMISSION_BASEURL"],
                        'record',
                        str(recid)
                    )
                    extra_data['recid'] = recid
                    workflow_object.set_extra_data(extra_data)
            # Will add the results to the engine extra_data column.
            workflow_object.continue_workflow(
                delayed=True,
                callback_results=callback_results
            )
            return jsonify({"result": "success"})
    return jsonify({"result": "failed"})


@blueprint.route('/workflows/webcoll', methods=['POST'])
def webcoll_callback():
    """Handle a callback from webcoll with the record ids processed.

    Expects the request data to contain a list of record ids in the
    recids field.
    """
    recids = dict(request.form).get('recids', [])
    pending_records = cache.get("pending_records") or dict()
    for rid in recids:
        if rid in pending_records:
            objectid = pending_records[rid]
            workflow_object = BibWorkflowObject.query.get(objectid)
            extra_data = workflow_object.get_extra_data()
            extra_data['url'] = join(cfg["CFG_ROBOTUPLOAD_SUBMISSION_BASEURL"], 'record', str(rid))
            extra_data['recid'] = rid
            workflow_object.set_extra_data(extra_data)
            workflow_object.continue_workflow(delayed=True)
            del pending_records[rid]
            cache.set("pending_records", pending_records,
                      timeout=cfg["PENDING_RECORDS_CACHE_TIMEOUT"])
    return jsonify({"result": "success"})


@blueprint.route('/workflows/robotupload', methods=['POST'])
def robotupload_callback():
    """Handle callback from robotupload.

    If robotupload was successful caches the workflow
    object id that corresponds to the uploaded record,
    so the workflow can be resumed when webcoll finish
    processing that record.
    If robotupload encountered an error sends an email
    to site administrator informing him about the error."""
    request_data = request.get_json()
    id_object = request_data.get("nonce", "")
    results = request_data.get("results", [])
    status = False
    for result in results:
        status = result.get('success', False)
        if status:
            recid = result.get('recid')
            pending_records = cache.get("pending_records") or dict()
            pending_records[str(recid)] = str(id_object)
            cache.set("pending_records", pending_records,
                      timeout=cfg["PENDING_RECORDS_CACHE_TIMEOUT"])
        else:
            from invenio.ext.email import send_email

            body = ("There was an error when uploading the "
                    "submission with id: %s.\n" % id_object)
            body += "Error message:\n"
            body += result.get('error_message', '')
            send_email(
                cfg["CFG_SITE_SUPPORT_EMAIL"],
                cfg["CFG_SITE_ADMIN_EMAIL"],
                'BATCHUPLOAD ERROR',
                body
            )
    return jsonify({"result": status})
