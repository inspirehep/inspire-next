#
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
#

from flask import Blueprint, jsonify, request
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
    """Handle callback from robotuploads to continue a workflow.

    Expects the request data to contain a object ID in the
    nonce field.
    """
    request_data = request.get_json()
    id_object = request_data.get("nonce", "")
    if id_object:
        callback_results = request_data.get("results", {})
        workflow_object = BibWorkflowObject.query.get(id_object)
        if workflow_object:
            # Will add the results to the engine extra_data column.
            workflow_object.continue_workflow(
                delayed=True,
                callback_results=callback_results
            )
            return jsonify({"result": "success"})
    return jsonify({"result": "failed"})
