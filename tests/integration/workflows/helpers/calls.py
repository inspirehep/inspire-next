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

from __future__ import absolute_import, division, print_function

import datetime
import json
import os

import pkg_resources

from invenio_accounts.testutils import login_user_via_session

from inspire_dojson import marcxml2record
from inspirehep.modules.workflows.utils import convert


def _call_workflow_resolve_api(app, workflow_id, data):
    """Calls to the workflow resolve endpoint.

    :param app: flask app to use
    :param workflow_id: id of the workflow to accept.
    :param action: action taken (normally on of 'reject', accept_core',
    'accept')
    """
    client = app.test_client()
    login_user_via_session(client, email='cataloger@inspirehep.net')
    return client.post(
        '/api/holdingpen/%s/action/resolve' % workflow_id,
        data=json.dumps(data),
        content_type='application/json',
    )


def do_resolve_workflow(app, workflow_id, action='accept_core'):
    data = {'value': action, 'id': workflow_id}
    response = _call_workflow_resolve_api(
        app=app,
        workflow_id=workflow_id,
        data=data
    )
    assert response.status_code == 200
    return response


def do_resolve_manual_merge_wf(app, workflow_id):
    """Accept one of the proposed matches."""
    response = _call_workflow_resolve_api(
        app=app,
        workflow_id=workflow_id,
        data=None
    )
    assert response.status_code == 200


def do_resolve_matching(app, workflow_id, match_id):
    data = {'match_recid': match_id}
    response = _call_workflow_resolve_api(
        app=app,
        workflow_id=workflow_id,
        data=data
    )
    assert response.status_code == 200


def do_accept_core(app, workflow_id):
    """Accepts the given workflow as core.

    :param app: flask app to use
    :param workflow_id: id of the workflow to accept.
    """
    response = do_resolve_workflow(
        app=app,
        workflow_id=workflow_id,
        action='accept_core',
    )
    response_data = json.loads(response.data)
    assert response_data == {
        'acknowledged': True,
        'action': 'resolve',
        'result': True,
    }


def do_robotupload_callback(
    app, workflow_id, recids, server_name='http://fake.na.me',
):
    """Calls to the robotupload callback with the given recids.

    :param app: flask app to use
    :param workflow_id: id of the associated workflow.
    :param recids: list of recids to generete the fake callback data.
    :param server_name: name of the server used for the record url.
    """
    client = app.test_client()
    data = {
        "nonce": workflow_id,
        "results": [
            {
                "recid": int(recid),
                "error_message": "",
                "success": True,
                "marcxml": "fake marcxml (not really used yet anywhere)",
                "url": "%s/record/%s" % (server_name, recid),
            } for recid in recids
        ],
    }

    response = client.post(
        '/callback/workflows/robotupload',
        data=json.dumps(data),
        content_type='application/json',
    )
    assert response.status_code == 200


def do_webcoll_callback(app, recids, server_name='http://fake.na.me'):
    """Calls to the webcoll callback with the given recids.

    :param app: flask app to use
    :param recids: list of recids to generete the fake callback data.
    :param server_name: name of the server used for the record url.
    """
    client = app.test_client()
    data = {"recids": recids}

    response = client.post(
        '/callback/workflows/webcoll',
        data=data,
        content_type='application/x-www-form-urlencoded',
    )
    assert response.status_code == 200


def generate_record():
    """Provide record fixture."""
    json_data = json.loads(pkg_resources.resource_string(
        __name__,
        os.path.join(
            '../fixtures',
            'oai_arxiv_core_record.json'
        )
    ))

    if 'preprint_date' in json_data:
        json_data['preprint_date'] = datetime.date.today().isoformat()

    return json_data


def core_record():
    """Provide record fixture."""
    record_oai_arxiv_plots = pkg_resources.resource_string(
        __name__,
        os.path.join(
            '../fixtures',
            'oai_arxiv_core_record.xml'
        )
    )
    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    json_data = marcxml2record(record_oai_arxiv_plots_marcxml)

    categories = {'core': [], 'non-core': []}
    for eprint in json_data.get('arxiv_eprints', []):
        categories['core'].extend(eprint.get('categories', []))

    if 'preprint_date' in json_data:
        json_data['preprint_date'] = datetime.date.today().isoformat()

    assert categories

    return json_data, categories


def do_validation_callback(app, worfklow_id, metadata, extra_data):
    """Do a validation callback request.

       Note:
           If ``malformed`` is true it will make the payload
           invalid, by removing two required ``keys``; ``id``
           and ``_extra_data``.
    """
    client = app.test_client()
    payload = {
        'id': worfklow_id,
        'metadata': metadata,
        '_extra_data': extra_data
    }

    return client.put(
        '/callback/workflows/resolve_validation_errors',
        data=json.dumps(payload),
        content_type='application/json',
    )
