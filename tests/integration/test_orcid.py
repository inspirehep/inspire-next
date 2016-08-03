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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from inspirehep.modules.orcid.models import InspireOrcidRecords

from inspirehep.utils.record_getter import get_db_record

from invenio_accounts.models import User

from invenio_db import db

from invenio_oauthclient.models import RemoteAccount, RemoteToken, UserIdentity

from invenio_search import current_search_client as es

import pytest


class OrcidApiMock(object):

    def __init__(self, put_code):
        self.put_code = put_code

    def add_record(self, author_orcid, token, category, orcid_json):
        return self.put_code

    def update_record(self, author_orcid, token, category, orcid_json, put_code):
        pass

    def remove_record(self, author_orcid, token, category, put_code):
        pass


class MockUser:

    def __init__(self, app):
        self.app = app


@pytest.fixture(scope="function")
def mock_user(app, request):

    def teardown(app):
        with app.app_context():
            user = User.query.filter_by(id=2).first()
            token = RemoteToken.query.filter_by(access_token='123').first()
            user_identity = UserIdentity.query.filter_by(
                id='0000-0001-9412-8627', method='orcid').first()
            remote_account = RemoteAccount.query.filter_by(user_id=2).first()
            with db.session.begin_nested():
                db.session.delete(token)
                db.session.delete(user_identity)
                db.session.delete(remote_account)
                db.session.delete(user)
            db.session.commit()

    request.addfinalizer(lambda: teardown(app))

    user = User(
        id=2,
    )
    token = RemoteToken(
        id_remote_account=1,
        access_token='123'
    )
    user_identity = UserIdentity(
        id='0000-0001-9412-8627',
        id_user='2',
        method='orcid')
    remote_account = RemoteAccount(
        id=1,
        user_id=2,
        extra_data={},
        client_id=1,
        user=user)
    with app.app_context():
        with db.session.begin_nested():
            db.session.add(user)
            db.session.add(user_identity)
            db.session.add(remote_account)
            db.session.add(token)
        db.session.commit()
    return MockUser(app)


@pytest.fixture(scope='function')
def orcid_test(mock_user, request):
    """Orcid test fixture."""
    app = mock_user.app

    def teardown(app):
        with app.app_context():
            es.delete(index='records-authors', doc_type='authors', id=10)

    record = {
        "name": {
            "status": "ACTIVE",
            "preferred_name": "Full Name",
            "value": "Full Name"
        },
        "$schema": "http://localhost:5000/schemas/records/authors.json",
        "control_number": "10",
        "self": {"$ref": "http://localhost:5000/api/authors/10"},
        "ids": [{
            "type": "INSPIRE",
            "value": "INSPIRE-0000000"
        },
            {
            "type": "ORCID",
            "value": "0000-0001-9412-8627"
        }],
        "self_recid": 10,
        "earliest_date": "2015-09-23"
    }

    request.addfinalizer(lambda: teardown(app))

    with app.app_context():
        es.index(index='records-authors',
                 doc_type='authors', id=10, body=record)
        es.indices.refresh('records-authors')
        record = get_db_record('literature', 782466)
        record['authors'].append({u'affiliations': [{u'value': u'St. Petersburg, INP'}],  u'curated_relation': True,  u'full_name': u'Full, Name',  u'profile': {
                                 u'__url__': u'http://inspirehep.net/record/00000000'},  u'record': {u'$ref': u'http://localhost:5000/api/authors/10'}})
        mock_orcid_api = OrcidApiMock(1)
        return mock_orcid_api, record


def test_record_is_sent_to_orcid(app, orcid_test):
    mock_orcid_api, record = orcid_test
    with app.app_context():
        from inspirehep.modules.orcid.tasks import send_to_orcid
        send_to_orcid(record, api=mock_orcid_api)

        expected = 1
        result = len(InspireOrcidRecords.query.all())

        assert result == expected


def test_record_is_deleted_from_orcid(app, orcid_test):
    mock_orcid_api, record = orcid_test
    with app.app_context():
        from inspirehep.modules.orcid.tasks import delete_from_orcid, send_to_orcid
        send_to_orcid(record, api=mock_orcid_api)
        delete_from_orcid(record, api=mock_orcid_api)

        expected = 0
        result = len(InspireOrcidRecords.query.all())

        assert result == expected
