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

"""Tests for arXiv workflows."""

from __future__ import absolute_import, division, print_function

import datetime
import json
import os
import pkg_resources
import re

import requests_mock
import mock
import pytest

from dojson.contrib.marc21.utils import create_record
from invenio_accounts.testutils import login_user_via_session
from invenio_db import db
from invenio_workflows import (
    ObjectStatus,
    WorkflowEngine,
    start,
    workflow_object_class,
)

from inspirehep.dojson.hep import hep
from inspirehep.factory import create_app
from inspirehep.modules.converter.xslt import convert
from inspirehep.modules.workflows.models import (
    WorkflowsAudit,
    WorkflowsPendingRecord,
)


@pytest.fixture(autouse=True)
def cleanup_workflows_tables(small_app):
    with small_app.app_context():
        obj_types = (
                WorkflowsAudit.query.all(),
                WorkflowsPendingRecord.query.all(),
                workflow_object_class.query(),
        )
        for obj_type in obj_types:
            for obj in obj_type:
                obj.delete()

        db.session.commit()


@pytest.fixture
def workflow_app():
    app = create_app(
        BEARD_API_URL="http://example.com/beard",
        DEBUG=True,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND='cache',
        CELERY_CACHE_BACKEND='memory',
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
        PRODUCTION_MODE=True,
        LEGACY_ROBOTUPLOAD_URL=(
            'http://localhost:1234'
        ),
        MAGPIE_API_URL="http://example.com/magpie",
        WTF_CSRF_ENABLED=False,
    )

    with app.app_context():
        yield app


@pytest.fixture
def record():
    """Provide record fixture."""
    record_oai_arxiv_plots = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_with_plots.xml'
        )
    )
    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    json_data = hep.do(record_marc)

    if 'preprint_date' in json_data:
        json_data['preprint_date'] = datetime.date.today().isoformat()

    return json_data


@pytest.fixture
def to_accept_record():
    """Provide record fixture."""
    record_oai_arxiv_plots = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_to_accept.xml'
        )
    )
    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    json_data = hep.do(record_marc)

    return json_data


@pytest.fixture
def already_harvested_on_legacy_record():
    """Provide record fixture."""
    record_oai_arxiv_plots = pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_already_on_legacy.xml'
        )
    )
    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    json_data = hep.do(record_marc)

    return json_data


def _do_resolve_workflow(app, workflow_id, action='accept_core'):
    """Calls to the workflow resolve endpoint.

    :param app: flask app to use
    :param workflow_id: id of the workflow to accept.
    :param action: action taken (normally on of 'reject', accept_core',
    'accept')
    """
    client = app.test_client()
    data = {
        'value': action,
        'id': workflow_id,
    }

    login_user_via_session(client, email='cataloger@inspirehep.net')
    return client.post(
        '/api/holdingpen/%s/action/resolve' % workflow_id,
        data=json.dumps(data),
        content_type='application/json',
    )


def _do_accept_core(app, workflow_id):
    """Accepts the given workflow as core.

    :param app: flask app to use
    :param workflow_id: id of the workflow to accept.
    """
    response = _do_resolve_workflow(
        app=app,
        workflow_id=workflow_id,
        action='accept_core',
    )
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data == {
        'acknowledged': True,
        'action': 'resolve',
        'result': True,
    }


def _do_robotupload_callback(
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
            ]
    }

    return client.post(
        '/callback/workflows/robotupload',
        data=json.dumps(data),
        content_type='application/json',
    )


def _do_webcoll_callback(app, recids, server_name='http://fake.na.me'):
    """Calls to the webcoll callback with the given recids.

    :param app: flask app to use
    :param recids: list of recids to generete the fake callback data.
    :param server_name: name of the server used for the record url.
    """
    client = app.test_client()
    data = {"recids": recids}

    return client.post(
        '/callback/workflows/webcoll',
        data=data,
        content_type='application/x-www-form-urlencoded',
    )


def fake_download_file(workflow, name, url):
    """Mock download_file_to_workflow func."""
    if url == 'http://arxiv.org/e-print/1407.7587':
        workflow.files[name] = pkg_resources.resource_stream(
            __name__,
            os.path.join(
                'fixtures',
                '1407.7587v1'
            )
        )
        return workflow.files[name]
    elif url == 'http://arxiv.org/pdf/1407.7587':
        workflow.files[name] = pkg_resources.resource_stream(
            __name__,
            os.path.join(
                'fixtures',
                '1407.7587v1.pdf',
            )
        )
        return workflow.files[name]
    raise Exception("Download file not mocked!")


def fake_beard_api_block_request(*args, **kwargs):
    """Mock json_api_request func."""
    return {}


def fake_beard_api_request(url, data):
    """Mock json_api_request func."""
    return {
        'decision': u'Non-CORE',
        'scores': [
            -0.20895982018928272, 0.8358207729691823, -1.6722188892559084
        ]
    }


def fake_magpie_api_request(url, data):
    """Mock json_api_request func."""
    if data.get('corpus') == 'experiments':
        return {
            'experiments': [
                {
                    'label': 'CMS',
                    'score': 0.75495152473449707,
                },
                {
                    'label': 'GEMS',
                    'score': 0.45495152473449707,
                },
                {
                    'label': 'ALMA',
                    'score': 0.39597576856613159,
                },
                {
                    'label': 'XMM',
                    'score': 0.28373843431472778,
                },
            ],
        }
    elif data.get('corpus') == 'categories':
        return {
            'categories': [
                {
                    'label': 'Astrophysics',
                    'score': 0.9941025972366333,
                },
                {
                    'label': 'Phenomenology-HEP',
                    'score': 0.0034253709018230438,
                },
                {
                    'label': 'Instrumentation',
                    'score': 0.0025460966862738132,
                },
                {
                    'label': 'Gravitation and Cosmology',
                    'score': 0.0017545684240758419,
                },
            ],
        }
    elif data.get('corpus') == 'keywords':
        return {
            'keywords': [
                {
                    'label': 'galaxy',
                    'score': 0.29424679279327393,
                },
                {
                    'label': 'numerical calculations',
                    'score': 0.22625420987606049,
                },
                {
                    'label': 'numerical calculations: interpretation of experiments',
                    'score': 0.031719371676445007,
                },
                {
                    'label': 'luminosity',
                    'score': 0.028066780418157578,
                },
                {
                    'label': 'experimental results',
                    'score': 0.027784878388047218,
                },
                {
                    'label': 'talk',
                    'score': 0.023392116650938988,
                },
            ],
        }


def fake_refextract_extract_references_from_file(*args, **kwargs):
    """Mock refextract extract_references_from_file func."""
    return {'references': []}


def get_halted_workflow(app, record, extra_config=None):
    extra_config = extra_config or {}
    with mock.patch.dict(app.config, extra_config):
        workflow_uuid = start('article', [record])

    eng = WorkflowEngine.from_uuid(workflow_uuid)
    obj = eng.processed_objects[0]

    assert obj.status == ObjectStatus.HALTED
    assert obj.data_type == "hep"

    # Files should have been attached (tarball + pdf, and plots)
    assert obj.files["1407.7587.pdf"]
    assert obj.files["1407.7587.tar.gz"]

    assert len(obj.files) > 2

    # A publication note should have been extracted
    pub_info = obj.data.get('publication_info')
    assert pub_info
    assert pub_info[0]
    assert pub_info[0].get('year') == 2014
    assert pub_info[0].get('journal_title') == "J. Math. Phys."

    # A prediction should have been made
    prediction = obj.extra_data.get("relevance_prediction")
    assert prediction
    assert prediction['decision'] == 'Non-CORE'
    assert prediction['scores']['Non-CORE'] == 0.8358207729691823

    expected_experiment_prediction = {
        'experiments': [
            {'label': 'CMS', 'score': 0.75495152473449707},
        ]
    }
    experiments_prediction = obj.extra_data.get("experiments_prediction")
    assert experiments_prediction == expected_experiment_prediction

    keywords_prediction = obj.extra_data.get("keywords_prediction")
    assert keywords_prediction
    assert {
        "label": "galaxy",
        "score": 0.29424679279327393,
        "accept": True
    } in keywords_prediction['keywords']

    # This record should not have been touched yet
    assert "approved" not in obj.extra_data

    return workflow_uuid, eng, obj


@mock.patch(
    'inspirehep.modules.workflows.utils.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.authors.receivers._query_beard_api',
    side_effect=fake_beard_api_block_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    side_effect=fake_refextract_extract_references_from_file,
)
def test_harvesting_arxiv_workflow_manual_rejected(
    mocked_refextract_extract_refs,
    mocked_api_request_beard_block,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download,
    small_app,
    record,
):
    """Test a full harvesting workflow."""

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid = None
    with small_app.app_context():
        workflow_uuid, eng, obj = get_halted_workflow(
            app=small_app,
            extra_config=extra_config,
            record=record,
        )

        # Now let's resolve it as accepted and continue
        # FIXME Should be accept, but record validation prevents us.
        obj.remove_action()
        obj.extra_data["approved"] = False
        # obj.extra_data["core"] = True
        obj.save()

        db.session.commit()

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]
        obj_id = obj.id
        obj.continue_workflow()

        obj = workflow_object_class.get(obj_id)
        # It was rejected
        assert obj.status == ObjectStatus.COMPLETED


@mock.patch(
    'inspirehep.modules.workflows.utils.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.authors.receivers._query_beard_api',
    side_effect=fake_beard_api_block_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    side_effect=fake_refextract_extract_references_from_file,
)
def test_harvesting_arxiv_workflow_already_on_legacy(
    mocked_refextract_extract_refs,
    mocked_api_request_beard_block,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download,
    small_app,
    already_harvested_on_legacy_record,
):
    """Test a full harvesting workflow."""

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid = None
    with small_app.app_context():
        with mock.patch.dict(small_app.config, extra_config):
            workflow_uuid = start('article', [
                already_harvested_on_legacy_record])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        assert obj.status == ObjectStatus.COMPLETED
        assert 'already-ingested' in obj.extra_data
        assert obj.extra_data['already-ingested']


@mock.patch(
    'inspirehep.modules.workflows.tasks.arxiv.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.utils.download_file_to_workflow',
    side_effect=fake_download_file,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.beard.json_api_request',
    side_effect=fake_beard_api_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.magpie.json_api_request',
    side_effect=fake_magpie_api_request,
)
@mock.patch(
    'inspirehep.modules.authors.receivers._query_beard_api',
    side_effect=fake_beard_api_block_request,
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.matching.search',
    return_value=[],
)
@mock.patch(
    'inspirehep.modules.workflows.tasks.refextract.extract_references_from_file',
    side_effect=fake_refextract_extract_references_from_file,
)
def test_harvesting_arxiv_workflow_manual_accepted(
    mocked_refextract_extract_refs,
    mocked_matching_search,
    mocked_api_request_beard_block,
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_download_utils,
    mocked_download_arxiv,
    workflow_app,
    record,
):
    """Test a full harvesting workflow."""
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile('.*(indexer|localhost).*'),
            real_http=True,
        )
        requests_mocker.register_uri(
            'POST',
            re.compile(
                'https?://localhost:1234.*',
            ),
            text=u'[INFO]',
            status_code=200,
        )

        workflow_uuid, eng, obj = get_halted_workflow(
            app=workflow_app,
            extra_config={'PRODUCTION_MODE': False},
            record=record,
        )

        _do_accept_core(
            app=workflow_app,
            workflow_id=obj.id,
        )

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]
        assert obj.status == ObjectStatus.WAITING

        response = _do_robotupload_callback(
            app=workflow_app,
            workflow_id=obj.id,
            recids=[12345],
        )
        assert response.status_code == 200

        obj = workflow_object_class.get(obj.id)
        assert obj.status == ObjectStatus.WAITING

        response = _do_webcoll_callback(app=workflow_app, recids=[12345])
        assert response.status_code == 200

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]
        # It was accepted
        assert obj.status == ObjectStatus.COMPLETED
