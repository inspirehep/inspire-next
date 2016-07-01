# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tests for arXiv workflows."""

from __future__ import absolute_import, division, print_function

import os

import mock

import pkg_resources
import pytest


@pytest.fixture
def record_oai_arxiv_plots():
    """Provide record fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_with_plots.xml'
        )
    )


@pytest.fixture
def record_oai_arxiv_accept():
    """Provide record fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'oai_arxiv_record_to_accept.xml'
        )
    )


@pytest.fixture
def some_record():
    """Provide record fixture."""
    return pkg_resources.resource_string(
        __name__,
        os.path.join(
            'fixtures',
            'some_record.xml'
        )
    )


@pytest.fixture
def arxiv_tarball():
    """Provide file fixture."""
    return pkg_resources.resource_filename(
        __name__,
        os.path.join(
            'fixtures',
            '1407.7587v1'
        )
    )


@pytest.fixture
def arxiv_pdf():
    """Provide file fixture."""
    return pkg_resources.resource_filename(
        __name__,
        os.path.join(
            'fixtures',
            '1407.7587v1.pdf'
        )
    )


@pytest.fixture
def arxiv_tarball_accept():
    """Provide file fixture."""
    return pkg_resources.resource_stream(
        __name__,
        os.path.join(
            'fixtures',
            '1511.01097'
        )
    )


@pytest.fixture
def arxiv_pdf_accept():
    """Provide file fixture."""
    return pkg_resources.resource_stream(
        __name__,
        os.path.join(
            'fixtures',
            '1511.01097v1.pdf'
        )
    )


def fake_download_file(obj, name, url):
    """Mock download_file func."""
    if url == 'http://arxiv.org/e-print/1407.7587':
        obj.files[name] = pkg_resources.resource_stream(
            __name__,
            os.path.join(
                'fixtures',
                '1407.7587v1'
            )
        )
        return obj.files[name]
    elif url == 'http://arxiv.org/pdf/1407.7587':
        obj.files[name] = pkg_resources.resource_stream(
            __name__,
            os.path.join(
                'fixtures',
                '1407.7587v1.pdf'
            )
        )
        return obj.files[name]
    raise Exception("Download file not mocked!")


def fake_beard_api_block_request(dummy):
    """Mock json_api_request func."""
    return {}


def fake_beard_api_request(url, data):
    """Mock json_api_request func."""
    return {
        'decision': u'Rejected',
        'scores': [
            -0.20895982018928272, -1.6722188892559084, 0.8358207729691823
        ]
    }


def fake_magpie_api_request(url, data):
    """Mock json_api_request func."""
    if data.get('corpus') == "experiments":
        return {
            "labels": [
                [
                    "CMS",
                    0.75495152473449707
                ],
                [
                    "GEMS",
                    0.45495152473449707
                ],
                [
                    "ALMA",
                    0.39597576856613159
                ],
                [
                    "XMM",
                    0.28373843431472778
                ],
            ],
            "status_code": 200
        }
    elif data.get('corpus') == "categories":
        return {
            "labels": [
                [
                    "Astrophysics",
                    0.9941025972366333
                ],
                [
                    "Phenomenology-HEP",
                    0.0034253709018230438
                ],
                [
                    "Instrumentation",
                    0.0025460966862738132
                ],
                [
                    "Gravitation and Cosmology",
                    0.0017545684240758419
                ],
            ],
            "status_code": 200
        }
    elif data.get('corpus') == "keywords":
        return {
            "labels": [
                [
                    "galaxy",
                    0.29424679279327393
                ],
                [
                    "numerical calculations",
                    0.22625420987606049
                ],
                [
                    "numerical calculations: interpretation of experiments",
                    0.031719371676445007
                ],
                [
                    "luminosity",
                    0.028066780418157578
                ],
                [
                    "experimental results",
                    0.027784878388047218
                ],
                [
                    "talk",
                    0.023392116650938988
                ],
            ],
            "status_code": 200
        }


@mock.patch('inspirehep.utils.helpers.download_file_to_record',
            side_effect=fake_download_file)
@mock.patch('inspirehep.modules.workflows.tasks.beard.json_api_request',
            side_effect=fake_beard_api_request)
@mock.patch('inspirehep.modules.workflows.tasks.magpie.json_api_request',
            side_effect=fake_magpie_api_request)
@mock.patch('inspirehep.modules.authors.receivers._query_beard_api',
            side_effect=fake_beard_api_block_request)
def test_harvesting_arxiv_workflow_rejected(
    mocked_api_request_beard_block, mocked_api_request_magpie,
    mocked_api_request_beard, mocked_download,
    app, record_oai_arxiv_plots):
    """Test a full harvesting workflow."""
    from invenio_workflows import (
        start, WorkflowEngine, ObjectStatus, workflow_object_class
    )
    from dojson.contrib.marc21.utils import create_record
    from invenio_db import db
    from inspirehep.dojson.hep import hep
    from inspirehep.modules.converter.xslt import convert

    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    record_json = hep.do(record_marc)

    extra_config = {
        "BEARD_API_URL": "http://example.com/beard",
        "MAGPIE_API_URL": "http://example.com/magpie",
    }

    workflow_uuid = None
    with app.app_context():
        with mock.patch.dict(app.config, extra_config):
            workflow_uuid = start('article', [record_json])

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
        assert pub_info[0].get('year') == "2014"
        assert pub_info[0].get('journal_title') == "J. Math. Phys."

        # A prediction should have been made
        prediction = obj.extra_data.get("relevance_prediction")
        assert prediction
        assert prediction['decision'] == "Rejected"
        assert prediction['scores']['Rejected'] == 0.8358207729691823

        experiments_prediction = obj.extra_data.get("experiments_prediction")
        assert experiments_prediction
        assert experiments_prediction['experiments'] == [
            ['CMS', 0.7549515247344971]
        ]

        keywords_prediction = obj.extra_data.get("keywords_prediction")
        assert keywords_prediction
        assert {"label": "galaxy", "score": 0.29424679279327393,
                "accept": True} in keywords_prediction['keywords']

        # This record should not have been touched yet
        assert "approved" not in obj.extra_data

        # Now let's resolve it as accepted and continue
        # FIXME Should be accept, but record validation prevents us.
        obj.remove_action()
        obj.extra_data["approved"] = False
        # obj.extra_data["core"] = True
        obj.save()

        db.session.commit()

    with app.app_context():
        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]
        obj_id = obj.id
        obj.continue_workflow()

        obj = workflow_object_class.get(obj_id)
        # It was rejected
        assert obj.status == ObjectStatus.COMPLETED


@pytest.mark.xfail(reason='record updates are busted due to validation issue')
@mock.patch('inspirehep.utils.arxiv.download_file_to_record',
            side_effect=fake_download_file)
def test_harvesting_arxiv_workflow_accepted(
    mocked, db_only_app, record_oai_arxiv_plots):
    """Test a full harvesting workflow."""
    from invenio_workflows import (
        start, WorkflowEngine, ObjectStatus, workflow_object_class
    )
    from dojson.contrib.marc21.utils import create_record
    from invenio_db import db
    from inspirehep.dojson.hep import hep
    from inspirehep.modules.converter.xslt import convert

    # Convert to MARCXML, then dict, then HEP JSON
    record_oai_arxiv_plots_marcxml = convert(
        record_oai_arxiv_plots,
        "oaiarXiv2marcxml.xsl"
    )
    record_marc = create_record(record_oai_arxiv_plots_marcxml)
    record_json = hep.do(record_marc)
    workflow_uuid = None
    with db_only_app.app_context():
        workflow_uuid = start('article', [record_json])

        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]

        assert obj.status == ObjectStatus.HALTED
        assert obj.data_type == "hep"

        # Files should have been attached (tarball + pdf)
        assert obj.files["1407.7587.pdf"]
        assert obj.files["1407.7587.tar.gz"]

        # A publication note should have been extracted
        pub_info = obj.data.get('publication_info')
        assert pub_info
        assert pub_info[0]
        assert pub_info[0].get('year') == "2014"
        assert pub_info[0].get('journal_title') == "J. Math. Phys."

        # This record should not have been touched yet
        assert "approved" not in obj.extra_data

        # Now let's resolve it as accepted and continue
        # FIXME Should be accept, but record validation prevents us.
        obj.remove_action()
        obj.extra_data["approved"] = True
        obj.extra_data["core"] = True
        obj.save()

        db.session.commit()

    with db_only_app.app_context():
        eng = WorkflowEngine.from_uuid(workflow_uuid)
        obj = eng.processed_objects[0]
        obj_id = obj.id
        obj.continue_workflow()

        obj = workflow_object_class.get(obj_id)
        # It was accepted
        assert obj.status == ObjectStatus.COMPLETED
