# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import mock

from invenio_workflows import (
    start,
    workflow_object_class,
)

from mocks import fake_beard_api_request, fake_download_file, fake_magpie_api_request
from workflow_utils import build_workflow


PUBLISHING_RECORD = {
    '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
    'titles': [
        {
            'title': 'Update without conflicts title.'
        },
    ],
    'arxiv_eprints': [
        {
            'categories': [
                'hep-lat',
                'hep-th'
            ],
            'value': '1703.04802'
        }
    ],
    'document_type': ['article'],
    '_collections': ['Literature'],
    'acquisition_source': {
        'datetime': '2020-11-12T04:49:13.369515',
        'method': 'hepcrawl',
        'submission_number': '978',
        'source': 'Elsevier',
    },
}

CURATION_RECORD = {
    '$schema': 'https://labs.inspirehep.net/schemas/records/hep.json',
    'titles': [
        {
            'title': 'Update without conflicts title.'
        },
    ],
    'arxiv_eprints': [
        {
            'categories': [
                'hep-lat',
                'hep-th'
            ],
            'value': '1703.04802'
        }
    ],
    'document_type': ['article'],
    '_collections': ['Literature'],
    'acquisition_source': {
        'datetime': '2020-11-12T04:49:13.369515',
        'method': 'hepcrawl',
        'submission_number': '978',
        'source': 'submitter',
    },
}


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.beard.json_api_request",
    side_effect=fake_beard_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_create_ticket_when_source_is_publishing(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):

    workflow_id = build_workflow(PUBLISHING_RECORD).id
    start("article", object_id=workflow_id)
    wf = workflow_object_class.get(workflow_id)
    ticket_publishing_content = u'content=Queue%3A+HEP_publishing'
    wf.continue_workflow()

    assert ticket_publishing_content in mocked_external_services.request_history[1].text
    assert wf.extra_data['curation_ticket_id']
    assert mocked_external_services.request_history[1].url == 'http://rt.inspire/ticket/new'


@mock.patch(
    "inspirehep.modules.workflows.tasks.actions.download_file_to_workflow",
    side_effect=fake_download_file,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.beard.json_api_request",
    side_effect=fake_beard_api_request,
)
@mock.patch(
    "inspirehep.modules.workflows.tasks.magpie.json_api_request",
    side_effect=fake_magpie_api_request,
)
def test_create_ticket_when_source_is_not_publishing(
    mocked_api_request_magpie,
    mocked_api_request_beard,
    mocked_package_download,
    workflow_app,
    mocked_external_services,
):

    workflow_id = build_workflow(CURATION_RECORD).id
    start("article", object_id=workflow_id)
    wf = workflow_object_class.get(workflow_id)
    ticket_curation_content = u'content=Queue%3A+HEP_curation'
    wf.continue_workflow()

    assert ticket_curation_content in mocked_external_services.request_history[1].text
    assert wf.extra_data['curation_ticket_id']
    assert mocked_external_services.request_history[1].url == 'http://rt.inspire/ticket/new'
