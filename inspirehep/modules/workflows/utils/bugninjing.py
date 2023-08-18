from __future__ import absolute_import, division, print_function

import re
from collections import OrderedDict
from itertools import chain

from flask import current_app
from invenio_db import db
from invenio_workflows import ObjectStatus, workflow_object_class
from invenio_workflows.models import WorkflowObjectModel
from invenio_workflows.errors import WorkflowsMissingObject


REGEEX_FIND_BLOCKING_WORKFLOWS = r"(?<=\>)\d{1,}(?=\<\/a\>)"
BLOCKED_WORKFLOWS_QUERY = "select id from workflows_object where extra_data ->> '_error_msg' ~ 'Cannot continue' and status = 5 and data -> 'acquisition_source' ->> 'source' = 'arXiv';"
VALIDATION_ERROR_WORKFLOWS_QUERY = "select id from workflows_object where extra_data ->> '_error_msg' ~ 'ValidationError' and status = 5 and data -> 'acquisition_source' ->> 'source' = 'arXiv';"


def get_blocking_workflows():
    errors = db.engine.execute(BLOCKED_WORKFLOWS_QUERY).fetchall()
    all_blocking_wfs = {}
    for wf_id in errors:
        wf = workflow_object_class.get(wf_id[0])
        msg = wf.extra_data["_error_msg"]
        matches = re.findall(REGEEX_FIND_BLOCKING_WORKFLOWS, msg)
        all_blocking_wfs[wf_id[0]] = [int(match) for match in matches]
    return all_blocking_wfs


def get_validation_errors():
    errors = db.engine.execute(VALIDATION_ERROR_WORKFLOWS_QUERY).fetchall()
    return errors


def get_halted_out_of_blocked(ids):
    halted_workflows = (
        db.session.query(WorkflowObjectModel.id)
        .filter(
            WorkflowObjectModel.status == ObjectStatus.HALTED,
            WorkflowObjectModel.id.in_(ids),
        )
        .all()
    )
    return halted_workflows


def get_workflows_for_curators():
    blocked_wfs = get_blocking_workflows()
    blocked_wfs = list(chain.from_iterable(blocked_wfs.values()))
    halted_workflows = get_halted_out_of_blocked(blocked_wfs)
    validation_errors = get_validation_errors()

    msg_payload = ""
    if halted_workflows:
        halted_wfs_payload = "\n*".join(
            [
                "{domain}/holdingpen{wf_id}".format(
                    domain=current_app.config["INSPIREHEP_URL"], wf_id=wf.id
                )
                for wf in halted_workflows
            ]
        )
        msg_payload += "Halted workflows:\n {}".format(halted_wfs_payload)

    if validation_errors:
        validation_errors_payload = "\n".join(
            [
                "{domain}/holdingpen{wf_id}".format(
                    domain=current_app.config["INSPIREHEP_URL"], wf_id=wf.id
                )
                for wf in validation_errors
            ]
        )
        msg_payload += "Validation errors:\n {}".format(validation_errors_payload)

    if msg_payload:
        return msg_payload


def get_error_chains(workflows, workflow_chain=None):
    if not workflow_chain:
        workflow_chain = []
    if isinstance(workflows, (int, str)):
        workflows = [workflows]
    for workflow in workflows:
        try:
            workflow = workflow_object_class.get(workflow)
        except WorkflowsMissingObject:  # workflow on blocking list, but doesn't exist amymore
            return workflow_chain
        msg = workflow.extra_data.get("_error_msg", "")
        if not msg or "Cannot continue processing workflow" not in msg:
            # put root error to the end of the list
            workflow_chain.append(
                workflow_chain.pop(workflow_chain.index(str(workflow.id)))
            )
            return workflow_chain
        matches = set(re.findall(REGEEX_FIND_BLOCKING_WORKFLOWS, msg))
        workflow_chain.extend(matches)
        get_error_chains(matches, workflow_chain)
    # remove duplicates keeping order at the same time
    return list(OrderedDict.fromkeys(workflow_chain))


def get_root_error():
    error_workflow_ids = db.engine.execute(BLOCKED_WORKFLOWS_QUERY).fetchall()
    msg_payload = ""
    for wf in error_workflow_ids:
        try:
            wf_id = wf[0]
            blocking_workflows = get_error_chains(wf_id)
            blocking_workflows.insert(0, str(wf_id))
            root_error_workflow = workflow_object_class.get(blocking_workflows[-1])
            workflow_information = (
                "->".join(blocking_workflows)
                + " root error status: {} ".format(root_error_workflow.status)
                + "root error task info: {}".format(
                    root_error_workflow.get_current_task_info()["nicename"]
                )
                + "\n------------------------"
            )
        except RuntimeError:  # circular dependency
            workflow_information = "Circular error dependency for wf {}".format(
                str(wf_id)
            )
        msg_payload += workflow_information
    return msg_payload
