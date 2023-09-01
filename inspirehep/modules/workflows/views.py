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

import copy
import re
from functools import wraps
from os.path import join

from flask import Blueprint, abort, current_app, jsonify, redirect, request
from flask.views import MethodView
from flask_login import current_user
from inspire_schemas.api import validate
from inspire_utils.record import get_value
from inspire_utils.urls import ensure_scheme
from invenio_db import db
from invenio_oauth2server.provider import oauth2
from invenio_workflows import (ObjectStatus, WorkflowEngine, start,
                               workflow_object_class)
from invenio_workflows.errors import WorkflowsMissingObject
from jsonschema.exceptions import ValidationError

from inspirehep.modules.records.permissions import RecordPermission
from inspirehep.modules.workflows.errors import (
    CallbackError, CallbackRecordNotFoundError, CallbackValidationError,
    CallbackWorkflowNotFoundError, CallbackWorkflowNotInMergeState,
    CallbackWorkflowNotInValidationError,
    CallbackWorkflowNotInWaitingEditState)
from inspirehep.modules.workflows.loaders import workflow_loader
from inspirehep.modules.workflows.models import WorkflowsPendingRecord
from inspirehep.modules.workflows.utils import (
    get_resolve_validation_callback_url, get_validation_errors)
from inspirehep.modules.workflows.utils.bugninjing import (
    get_root_error, get_workflows_for_curators)
from inspirehep.utils.record_getter import RecordGetterError, get_db_record
from inspirehep.utils.tickets import get_rt_link_for_ticket

callback_blueprint = Blueprint(
    "inspire_workflows_callbacks",
    __name__,
    url_prefix="/callback",
    template_folder="templates",
    static_folder="static",
)


workflow_blueprint = Blueprint(
    "inspire_workflows",
    __name__,
    url_prefix="/workflows",
    template_folder="templates",
    static_folder="static",
)


def require_api_auth():
    """
    Decorator to require API authentication using OAuth token.
    """

    def wrapper(f):
        f_oauth_required = oauth2.require_oauth()(f)

        @wraps(f)
        def decorated(*args, **kwargs):
            return f_oauth_required(*args, **kwargs)

        return decorated

    return wrapper


def login_required_with_roles(roles=None):
    """Login required with roles decorator.

    :param roles (list(str)): a list of roles names.
    """

    def wrapper_function(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)

            if roles:
                # superuser can do everything
                user_roles = {role.name for role in current_user.roles}
                has_access = user_roles & set(roles)
                if not has_access:
                    abort(403)
            return func(*args, **kwargs)

        return wrapped_function

    return wrapper_function


@callback_blueprint.errorhandler(CallbackError)
@workflow_blueprint.errorhandler(CallbackError)
def error_handler(error):
    """Callback error handler."""
    response = jsonify(error.to_dict())
    return response, error.code


def _continue_workflow(workflow_id, recid, result=None):
    """Small wrapper to continue a workflow.

    Will prepare the needed data from the record id and the result data if
    passed.

    :return: True if succeeded, False if the specified workflow id does not
        exist.
    """
    result = result if result is not None else {}
    base_url = ensure_scheme(current_app.config["SERVER_NAME"])
    try:
        workflow_object = workflow_object_class.get(workflow_id)
    except WorkflowsMissingObject:
        current_app.logger.error(
            "No workflow object with the id %s could be found.",
            workflow_id,
        )
        return False

    workflow_object.extra_data["url"] = join(base_url, "record", str(recid))
    workflow_object.extra_data["recid"] = recid
    workflow_object.data["control_number"] = recid
    workflow_object.extra_data["callback_result"] = result
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
            "The workflow %s was not found.",
            workflow_id,
        )
        return {
            "success": False,
            "message": "workflow with id %s not found." % workflow_id,
        }

    return {
        "success": True,
        "message": "workflow with id %s continued." % workflow_id,
    }


def _put_workflow_in_error_state(workflow_id, error_message, result):
    try:
        workflow_object = workflow_object_class.get(workflow_id)
    except WorkflowsMissingObject:
        current_app.logger.error(
            "No workflow object with the id %s could be found.",
            workflow_id,
        )
        return {
            "success": False,
            "message": "workflow with id %s not found." % workflow_id,
        }

    workflow_object.status = ObjectStatus.ERROR
    workflow_object.extra_data["callback_result"] = result
    workflow_object.extra_data["_error_msg"] = error_message
    workflow_object.save()
    db.session.commit()

    return {
        "success": True,
        "message": "workflow %s updated with error." % workflow_id,
    }


@callback_blueprint.route("/workflows/webcoll", methods=["POST"])
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
    recids = dict(request.form).get("recids", [])
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
        if continue_response["success"]:
            current_app.logger.debug(
                "Successfully restarted workflow %s",
                workflow_id,
            )
            response[recid] = {
                "success": True,
                "message": "Successfully restarted workflow %s" % workflow_id,
            }
        else:
            current_app.logger.debug(
                "Error restarting workflow %s: %s",
                workflow_id,
                continue_response["message"],
            )
            response[recid] = {
                "success": False,
                "message": continue_response["message"],
            }

        db.session.delete(pending_record)
        db.session.commit()

    return jsonify(response)


def _robotupload_has_error(result):
    recid = int(result.get("recid"))
    if not result.get("success"):
        message = result.get("error_message", "No error message from robotupload.")
    elif recid < 0:
        message = result.get(
            "error_message",
            "Failed to create record on robotupload.",
        )
    else:
        return False, ""

    return True, message


def _is_an_update(workflow_id):
    workflow_object = workflow_object_class.get(workflow_id)
    return bool(workflow_object.extra_data.get("is-update"))


def _is_an_authors_workflow(workflow_id):
    workflow_object = workflow_object_class.get(workflow_id)
    return workflow_object.data.get("_collections") == "Authors"


def _parse_robotupload_result(result, workflow_id):
    response = {}
    recid = int(result.get("recid"))

    result_has_error, error_message = _robotupload_has_error(result)
    if result_has_error:
        response = {
            "success": False,
            "message": error_message,
        }
        return response

    if _is_an_authors_workflow(workflow_id):
        already_pending_ones = WorkflowsPendingRecord.query.filter_by(
            record_id=recid,
        ).all()
        if already_pending_ones:
            current_app.logger.warning(
                "The record %s was already found on the pending list.", recid
            )
            response = {
                "success": False,
                "message": "Recid %s already in pending list." % recid,
            }
            return response

        if not _is_an_update(workflow_id):
            pending_entry = WorkflowsPendingRecord(
                workflow_id=workflow_id,
                record_id=recid,
            )
            db.session.add(pending_entry)
            db.session.commit()

            current_app.logger.debug(
                "Successfully added recid:workflow %s:%s to pending list.",
                recid,
                workflow_id,
            )

    continue_response = _find_and_continue_workflow(
        workflow_id=workflow_id,
        recid=recid,
        result=result,
    )
    if continue_response["success"]:
        current_app.logger.debug(
            "Successfully restarted workflow %s",
            workflow_id,
        )
        response = {
            "success": True,
            "message": "Successfully restarted workflow %s" % workflow_id,
        }
    else:
        current_app.logger.debug(
            "Error restarting workflow %s: %s",
            workflow_id,
            continue_response["message"],
        )
        response = {
            "success": False,
            "message": continue_response["message"],
        }

    return response


@callback_blueprint.route("/workflows/robotupload", methods=["POST"])
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
    workflow_id = request_data.get("nonce", "")
    results = request_data.get("results", [])
    responses = {}
    for result in results:
        recid = int(result.get("recid"))

        if recid in responses:
            # this should never happen
            current_app.logger.warning("Received duplicated recid: %s", recid)
            continue

        response = _parse_robotupload_result(
            result=result,
            workflow_id=workflow_id,
        )
        if not response["success"]:
            error_set_result = _put_workflow_in_error_state(
                workflow_id=workflow_id,
                error_message="Error in robotupload: %s" % response["message"],
                result=result,
            )
            if not error_set_result["success"]:
                response["message"] += (
                    "\nFailed to put the workflow in error state:%s"
                    % error_set_result["message"]
                )

        responses[recid] = response

    return jsonify(responses)


def _validate_workflow_schema(workflow_data):
    """Validate the ``metadata`` against the ``hep`` JSONSchema.

    Args:
        workflow_data (dist): the workflow dict.

    Raises:
        CallbackValidationError: if the workflow ``metadata`` is not valid
            against ``hep`` JSONSchema.
    """

    # Check for validation errors
    try:
        validate(workflow_data["metadata"])
    except ValidationError:
        workflow_data["_extra_data"]["validation_errors"] = get_validation_errors(
            workflow_data["metadata"], "hep"
        )
        workflow_data["_extra_data"][
            "callback_url"
        ] = get_resolve_validation_callback_url()
        raise CallbackValidationError(workflow_data)


class ResolveMergeResource(MethodView):
    """Resolve merge callback.

    When the workflow needs to resolve conficts, the workflow stops in
    ``HALTED`` state, to continue this endpoint is called. If it's called
    and the conflicts are not resolved it will just save the workflow.

    Args:
        workflow_data (dict): the workflow object send in the request's payload.

    """

    def put(self):
        """Handle callback for merge conflicts."""
        workflow_data = workflow_loader()
        workflow_id = workflow_data["id"]

        try:
            workflow = workflow_object_class.get(workflow_id)
        except WorkflowsMissingObject:
            raise CallbackWorkflowNotFoundError(workflow_id)

        if (
            workflow.status != ObjectStatus.HALTED
            or "callback_url" not in workflow.extra_data
        ):
            raise CallbackWorkflowNotInMergeState(workflow.id)

        conflicts = get_value(workflow_data["_extra_data"], "conflicts", default=[])

        workflow.data = workflow_data["metadata"]
        workflow.extra_data["conflicts"] = conflicts

        if not conflicts:
            workflow.status = ObjectStatus.RUNNING

            workflow.extra_data.pop("callback_url", None)
            workflow.extra_data.pop("conflicts", None)

            workflow.save()
            db.session.commit()
            workflow.continue_workflow(delayed=True)

            data = {
                "message": "Workflow {} is continuing.".format(workflow.id),
            }
            return jsonify(data), 200

        # just save
        data = {
            "message": "Workflow {} has been saved with conflicts.".format(workflow.id),
        }
        workflow.save()
        db.session.commit()

        return jsonify(data), 200


class ResolveValidationResource(MethodView):
    """Resolve validation error callback."""

    def put(self):
        """Handle callback from validation errors.

        When validation errors occur, the workflow stops in ``ERROR`` state, to
        continue this endpoint is called.

        Args:
            workflow_data (dict): the workflow object send in the
                request's payload.

        Examples:
            An example of successful call:

                $ curl \\
                    http://web:5000/callback/workflows/resolve_validation_errors \\
                    -H "Host: localhost:5000" \\
                    -H "Content-Type: application/json" \\
                    -d '{
                        "_extra_data": {
                            ... extra data content
                        },
                        "id": 910648,
                        "metadata": {
                            "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
                            ... record content
                        }
                    }'

            The response:

                HTTP 200 OK

                {"mesage": "Workflow 910648 validated, continuing it."}


            A failed example:

                $ curl \\
                    http://web:5000/callback/workflows/resolve_validation_errors \\
                    -H "Host: localhost:5000" \\
                    -H "Content-Type: application/json" \\
                    -d '{
                        "_extra_data": {
                            ... extra data content
                        },
                        "id": 910648,
                        "metadata": {
                            "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
                            ... record content
                        }
                    }'

            The error response will contain the workflow that was passed, with the
            new validation errors:

                HTTP 400 Bad request

                {
                    "_extra_data": {
                        "validatior_errors": [
                            {
                                "path": ["path", "to", "error"],
                                "message": "required: ['missing_key1', 'missing_key2']"
                            }
                        ],
                        ... rest of extra data content
                    },
                    "id": 910648,
                    "metadata": {
                        "$schema": "https://labs.inspirehep.net/schemas/records/hep.json",
                        ... record content
                    }
                }
        """
        workflow_data = workflow_loader()
        _validate_workflow_schema(workflow_data)

        workflow_id = workflow_data["id"]
        try:
            workflow = workflow_object_class.get(workflow_id)
        except WorkflowsMissingObject:
            raise CallbackWorkflowNotFoundError(workflow_id)

        if (
            workflow.status != ObjectStatus.ERROR
            or "callback_url" not in workflow.extra_data
        ):
            raise CallbackWorkflowNotInValidationError(workflow_id)

        workflow.data = workflow_data["metadata"]
        workflow.status = ObjectStatus.RUNNING

        workflow.extra_data.pop("callback_url", None)
        workflow.extra_data.pop("validation_errors", None)

        workflow.save()
        db.session.commit()
        workflow.continue_workflow(delayed=True)

        data = {
            "message": "Workflow {} is continuing.".format(workflow.id),
        }
        return jsonify(data), 200


class ResolveEditArticleResource(MethodView):
    """Resolve `edit_article` callback.

    When the workflow needs to resolve conficts, the workflow stops in
    ``HALTED`` state, to continue this endpoint is called. If it's called
    and the conflicts are not resolved it will just save the workflow.

    Args:
        workflow_data (dict): the workflow object send in the request's payload.

    """

    def put(self):
        """Handle callback for merge conflicts."""
        workflow_data = workflow_loader()
        workflow_id = workflow_data["id"]

        try:
            workflow = workflow_object_class.get(workflow_id)
        except WorkflowsMissingObject:
            raise CallbackWorkflowNotFoundError(workflow_id)

        if (
            workflow.status != ObjectStatus.WAITING
            or "callback_url" not in workflow.extra_data
        ):
            raise CallbackWorkflowNotInWaitingEditState(workflow.id)

        recid = workflow_data["metadata"].get("control_number")
        try:
            record = get_db_record("lit", recid)
        except RecordGetterError:
            raise CallbackRecordNotFoundError(recid)

        record_permission = RecordPermission.create(action="update", record=record)
        if not record_permission.can():
            abort(403, record_permission)

        workflow_id = workflow.id
        workflow.data = workflow_data["metadata"]
        workflow.status = ObjectStatus.RUNNING
        workflow.extra_data.pop("callback_url", None)
        workflow.save()
        db.session.commit()
        workflow.continue_workflow(delayed=True)

        data = {"message": "Workflow {} is continuing.".format(workflow_id)}
        ticket_id = workflow_data["_extra_data"].get("curation_ticket_id")
        if ticket_id:
            data["redirect_url"] = get_rt_link_for_ticket(ticket_id)

        return jsonify(data), 200


def start_edit_article_workflow(recid):
    try:
        record = get_db_record("lit", recid)
    except RecordGetterError:
        raise CallbackRecordNotFoundError(recid)

    record_permission = RecordPermission.create(action="update", record=record)
    if not record_permission.can():
        abort(403, record_permission)
    # has to be done before start() since, it is deattaching this session
    user_id = current_user.get_id()
    eng_uuid = start("edit_article", data=record)
    workflow_id = WorkflowEngine.from_uuid(eng_uuid).objects[0].id
    workflow = workflow_object_class.get(workflow_id)
    workflow.id_user = user_id
    if request.referrer:
        base_rt_url = get_rt_link_for_ticket("").replace("?", "\?")
        ticket_match = re.match(base_rt_url + "(?P<ticket_id>\d+)", request.referrer)
        if ticket_match:
            ticket_id = int(ticket_match.group("ticket_id"))
            workflow.extra_data["curation_ticket_id"] = ticket_id

    workflow.save()
    db.session.commit()
    url = "{}{}".format(current_app.config["WORKFLOWS_EDITOR_API_URL"], workflow_id)
    return redirect(location=url, code=302)


@workflow_blueprint.route("/inspect_merge/<int:holdingpen_id>", methods=["GET"])
def inspect_merge(holdingpen_id):
    wf = workflow_object_class.get(holdingpen_id)
    revision_id = wf.extra_data.get("merger_head_revision", None)
    if revision_id is None:
        abort(400, "Cannot inspect merge operation on this workflow")

    root = wf.extra_data.get("merger_original_root")
    update = wf.extra_data["merger_root"]
    merged = get_db_record("lit", wf.data["control_number"])
    # XXX merged.revisions[revision_id] should work if not for the messed up
    # non-consecutive versions in prod
    head = merged.model.versions.filter_by(version_id=(revision_id + 1)).one().json

    return jsonify(root=root, head=head, update=update, merged=merged)


@workflow_blueprint.route("/authors", methods=["POST"])
@require_api_auth()
def start_workflow_for_author_submission():
    submission_data = request.get_json()["data"]
    workflow_object = workflow_object_class.create(
        data={},
        id_user=submission_data["acquisition_source"]["internal_uid"],
        data_type="authors",
    )
    submission_data["acquisition_source"]["submission_number"] = str(workflow_object.id)
    workflow_object.data = submission_data
    workflow_object.extra_data["is-update"] = bool(
        submission_data.get("control_number")
    )
    workflow_object.extra_data["source_data"] = {
        "data": copy.deepcopy(workflow_object.data),
        "extra_data": copy.deepcopy(workflow_object.extra_data),
    }

    workflow_object.save()
    db.session.commit()

    workflow_object_id = workflow_object.id

    start.delay("author", object_id=workflow_object.id)

    return jsonify({"workflow_object_id": workflow_object_id})


@workflow_blueprint.route("/literature", methods=["POST"])
@require_api_auth()
def start_workflow_for_literature_submission():
    json = request.get_json()
    submission_data = json["data"]

    workflow_object = workflow_object_class.create(
        data={},
        id_user=submission_data["acquisition_source"]["internal_uid"],
        data_type="hep",
    )
    submission_data["acquisition_source"]["submission_number"] = str(workflow_object.id)
    workflow_object.data = submission_data
    workflow_object.extra_data["formdata"] = json["form_data"]

    # Add submission pdf from formdata.url
    form_url = workflow_object.extra_data["formdata"].get("url")
    if form_url and "arxiv.org" not in form_url:
        workflow_object.extra_data["submission_pdf"] = form_url

    # Remember that source_data should be created at the end, with all fields already
    # filled. As first step in WF will overwrite everything with data form source_data
    workflow_object.extra_data["source_data"] = {
        "extra_data": copy.deepcopy(workflow_object.extra_data),
        "data": copy.deepcopy(workflow_object.data),
    }

    workflow_object.save()
    db.session.commit()

    workflow_object_id = workflow_object.id

    start.delay("article", object_id=workflow_object.id)

    return jsonify({"workflow_object_id": workflow_object_id})


@workflow_blueprint.route("/bugninja/get-workflows-for-curator", methods=["GET"])
@login_required_with_roles(["chatbot", "superuser"])
def get_workflows_for_curator():
    message = get_workflows_for_curators()
    return jsonify({"message": message})


@workflow_blueprint.route("/bugninja/get-workflows-root-error", methods=["GET"])
@login_required_with_roles(["chatbot", "superuser"])
def get_workflows_root_error():
    message = get_root_error()
    return jsonify({"message": message})


callback_resolve_validation = ResolveValidationResource.as_view(
    "callback_resolve_validation"
)
callback_resolve_merge_conflicts = ResolveMergeResource.as_view(
    "callback_resolve_merge_conflicts"
)
callback_resolve_edit_article = ResolveEditArticleResource.as_view(
    "callback_resolve_edit_article"
)

callback_blueprint.add_url_rule(
    "/workflows/resolve_validation_errors",
    view_func=callback_resolve_validation,
)
callback_blueprint.add_url_rule(
    "/workflows/resolve_merge_conflicts",
    view_func=callback_resolve_merge_conflicts,
)
workflow_blueprint.add_url_rule(
    "/edit_article/<recid>",
    view_func=start_edit_article_workflow,
)
callback_blueprint.add_url_rule(
    "/workflows/resolve_edit_article", view_func=callback_resolve_edit_article
)
