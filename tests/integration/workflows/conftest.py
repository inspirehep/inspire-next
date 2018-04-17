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

import os
import re
import pytest
import requests_mock
import sys

from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from invenio_search.cli import current_search_client as es

from inspirehep.factory import create_app
from inspirehep.modules.fixtures.collections import init_collections
from inspirehep.modules.fixtures.files import init_all_storage_paths
from inspirehep.modules.fixtures.users import init_users_and_permissions
from inspirehep.modules.records.api import InspireRecord

# Use the helpers folder to store test helpers.
# See: http://stackoverflow.com/a/33515264/374865
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))


@pytest.fixture
def workflow_app():
    """Flask application with no records and function scope.

    .. deprecated:: 2017-09-18
       Use ``app`` instead.
    """
    RT_URL = "http://rt.inspire"

    with requests_mock.Mocker() as m:
        m.register_uri(
            requests_mock.ANY,
            re.compile('.*' + RT_URL + '.*'),
            status_code=200,
            text='Status 200'
        )

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
            WORKFLOWS_MATCH_REMOTE_SERVER_URL="http://legacy_search.endpoint/",
            WORKFLOWS_FILE_LOCATION="/",
            WTF_CSRF_ENABLED=False,
            CFG_BIBCATALOG_SYSTEM_RT_URL=RT_URL
        )

    with app.app_context():
        yield app


def drop_all(app):
    db.drop_all()
    _es = app.extensions['invenio-search']
    list(_es.delete(ignore=[404]))


def create_all(app):
    db.create_all()
    _es = app.extensions['invenio-search']
    list(_es.create(ignore=[400]))

    init_all_storage_paths()
    init_users_and_permissions()
    init_collections()


@pytest.fixture(autouse=True)
def cleanup_workflows(workflow_app):
    db.session.close_all()
    drop_all(app=workflow_app)
    create_all(app=workflow_app)


@pytest.fixture
def mocked_external_services(workflow_app):
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
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['WORKFLOWS_MATCH_REMOTE_SERVER_URL'] +
                '.*'
            ),
            status_code=200,
            json=[],
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['BEARD_API_URL'] +
                '/text/phonetic_blocks.*'
            ),
            status_code=200,
            json={'phonetic_blocks': {}},
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['CFG_BIBCATALOG_SYSTEM_RT_URL'] +
                '/ticket/new.*'
            ),
            status_code=200,
            text='RT/3.8.7 200 Ok\n\n# Ticket 1 created.\n# Ticket 1 updated.'
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['CFG_BIBCATALOG_SYSTEM_RT_URL'] +
                '/ticket/.*/comment'
            ),
            status_code=200,
        )
        requests_mocker.register_uri(
            requests_mock.ANY,
            re.compile(
                '.*' +
                workflow_app.config['CFG_BIBCATALOG_SYSTEM_RT_URL'] +
                '/ticket/.*/edit'
            ),
            status_code=200,
            text='Irrelevant part 1 of message \nIrrelevant part 2 of message \n# Ticket 1 updated.'
        )

        yield


@pytest.fixture
def record_from_db(workflow_app):
    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'Fancy title for a new record'}],
        'arxiv_eprints': [
            {'categories': ['hep-th'], 'value': '1407.7587'}
        ],
        'control_number': 1234,
        'authors': [
            {'full_name': 'Maldacena, J.'},
            {'full_name': 'Strominger, A.'},
        ],
        'abstracts': [
            {'source': 'arxiv', 'value': 'A basic abstract.'}
        ],
        'report_numbers': [{'value': 'DESY-17-036'}]
    }
    record = InspireRecord.create(json, id_=None, skip_files=True)
    record.commit()
    rec_uuid = record.id

    db.session.commit()
    es.indices.refresh('records-hep')

    yield record

    record = InspireRecord.get_record(rec_uuid)
    pid = PersistentIdentifier.get(
        pid_type='lit',
        pid_value=record['control_number']
    )

    pid.unassign()
    pid.delete()
    record.delete()
    record.commit()
