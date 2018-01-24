# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""ORCID util tests."""

from __future__ import absolute_import, division, print_function

import mock
import os
import pkg_resources
import pytest
import requests_mock

from flask import current_app
from lxml import etree
from orcid.orcid import MemberAPI

from invenio_db import db
from invenio_oauthclient.utils import oauth_link_external_id
from invenio_oauthclient.models import (
    RemoteAccount,
    RemoteToken,
    User,
    UserIdentity,
)

from inspire_utils.record import get_value
from inspirehep.utils.record_getter import get_db_record
from inspirehep.modules.orcid.utils import (
    _find_put_code_for_record_in_orcid,
    _get_author_orcids_for_record,
    _get_put_code,
    _recid_from_url,
    _hep_orcid_records_matching,
    _oauth_token_for_orcid,
    _orcid_hep_publication_info_matching,
    _was_record_pushed_by_inspire,
    push_record_to_all,
    push_record_with_orcid,
)


def get_xml(works_file):
    """Get and parse an XML file from ./fixtures directory"""
    work_path = pkg_resources.resource_filename(
        __name__,
        os.path.join('fixtures', works_file)
    )
    return etree.parse(work_path).getroot()


def get_works_group(works_file):
    """Get the first activities:group node from works"""
    sample_works = get_xml(works_file)
    return sample_works.xpath(
        '/activities:works/activities:group',
        namespaces=sample_works.nsmap
    )[0]


@pytest.fixture(scope='module')
def with_fake_credentials():
    """Fake ORCID_APP_CREDENTIALS"""
    extra_config = {
        'ORCID_APP_CREDENTIALS': {
            'consumer_key': '0000-0002-3874-0886',
            'consumer_secret': '01234567-89ab-cdef-0123-456789abcdef',
        },
    }
    with mock.patch.dict(current_app.config, extra_config):
        yield


@pytest.fixture
def mock_api_common(with_fake_credentials):
    """Yield a MemberAPI and mock responses"""
    api = MemberAPI(
        current_app.config['ORCID_APP_CREDENTIALS']['consumer_key'],
        current_app.config['ORCID_APP_CREDENTIALS']['consumer_secret']
    )
    with requests_mock.mock() as m:
        yield api, m


@pytest.fixture
def mock_api(mock_api_common):
    """Yield a MemberAPI with fake responses"""
    api, m = mock_api_common
    m.get(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/works',
        text=etree.tostring(get_xml('works.xml')),
        headers={'Content-Type': 'application/orcid+xml'},
    )
    m.put(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/work/895497',
        text='200 OK'
    )
    m.get(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/work/895497',
        text=etree.tostring(get_xml('work.xml')),
        headers={'Content-Type': 'application/orcid+xml'}
    )
    return api


@pytest.fixture
def mock_api_no_match(mock_api_common):
    """Yield a MemberAPI with fake responses"""
    api, m = mock_api_common
    m.get(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/works',
        text=etree.tostring(get_xml('works_no_match.xml')),
        headers={'Content-Type': 'application/orcid+xml'},
    )
    m.get(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/work/123456',
        text=etree.tostring(get_xml('work_no_match.xml')),
        headers={'Content-Type': 'application/orcid+xml'}
    )
    m.post(
        'https://api.orcid.org/v2.0/0000-0002-1825-0097/work',
        headers={
            'Location': 'https://api.orcid.org/v2.0/0000-0002-1825-0097/'
                        'work/123456'
        },
    )
    return api


@pytest.fixture(scope='module')
def db_setup_and_teardown(with_fake_credentials):
    # Dummy variables
    TOKEN = '00000000-0000-0000-0000-000000000000'
    EMAIL = 'josiah.carberry@example.com'
    NAME = 'Josiah Carberry'
    ORCID = '0000-0002-1825-0097'

    # Create a dummy User
    user = User()
    user.email = EMAIL

    with db.session.begin_nested():
        db.session.add(user)

    # Link the user with an example ORCID
    oauth_link_external_id(user, {
        'id': ORCID,
        'method': 'orcid'
    })

    # Link the user to the token
    with db.session.begin_nested():
        db.session.add(RemoteToken.create(
            user_id=user.id,
            client_id=get_value(
                current_app.config, 'ORCID_APP_CREDENTIALS.consumer_key'
            ),
            token=TOKEN,
            secret=None,
            extra_data={
                'orcid': ORCID,
                'full_name': NAME,
            }
        ))

    # Run the test
    yield

    # Cleanup
    RemoteToken.query.filter_by(access_token=TOKEN).delete()

    user_id = db.session.query(UserIdentity.id_user).filter(
        UserIdentity.id == ORCID
    ).subquery()

    RemoteAccount.query.filter(
        RemoteAccount.user_id.in_(user_id)
    ).delete(
        synchronize_session='fetch'
    )

    UserIdentity.query.filter_by(id=ORCID).delete()
    User.query.filter_by(email=EMAIL).delete()


@pytest.mark.parametrize('sample_group', [get_works_group('works.xml')])
def test_was_record_pushed_by_inspire(sample_group, with_fake_credentials):
    assert _was_record_pushed_by_inspire(sample_group)


@pytest.mark.parametrize('sample_group', [
    get_works_group('works.xml'),
    get_works_group('works_no_doi.xml')
])
def test_hep_orcid_records_matching(sample_group, mock_api):
    sample_matching_hep = get_db_record('lit', 4328)
    assert _hep_orcid_records_matching(
        sample_matching_hep,
        sample_group,
        '0000-0002-1825-0097',
        'fake-token',
        mock_api
    )


@pytest.mark.parametrize('url, expected', [
    ('https://inspirehep.net/record/1373790', 1373790),
    ('http://inspirehep.net/record/1373790', 1373790),
    ('https://inspirehep.net/literature/1373790', 1373790),
    ('https://labs.inspirehep.net/literature/1373790', 1373790),
    ('https://not-inspire.net/literature/1373790', None),
    ('http://definitely-not-inspire.com', None),
])
def test_recid_from_url(url, expected):
    result = _recid_from_url(url)
    assert result == expected


def test_oauth_token_for_orcid(db_setup_and_teardown):
    expected = '00000000-0000-0000-0000-000000000000'
    result = _oauth_token_for_orcid('0000-0002-1825-0097')

    assert expected == result


@pytest.mark.parametrize('sample_group', [get_works_group('works.xml')])
def test_get_put_code(sample_group):
    expected = '895497'
    result = _get_put_code(sample_group)

    assert expected == result


def test_find_put_code_for_record_in_orcid(mock_api):
    sample_hep = get_db_record('lit', 4328)

    expected = '895497'
    result = _find_put_code_for_record_in_orcid(
        record=sample_hep,
        orcid='0000-0002-1825-0097',
        oauth_token='fake-token',
        api=mock_api
    )

    assert expected == result


def test_push_record_with_orcid(db_setup_and_teardown, mock_api):
    sample_hep = get_db_record('lit', 4328)
    sample_orcid = '0000-0002-1825-0097'

    push_record_with_orcid(sample_hep, sample_orcid)


def test_push_record_with_orcid_no_match(db_setup_and_teardown, mock_api_no_match):
    sample_hep = get_db_record('lit', 4328)
    sample_orcid = '0000-0002-1825-0097'

    push_record_with_orcid(sample_hep, sample_orcid)


def test_orcid_hep_publication_info_matching():
    sample_work = get_xml('work.xml')
    sample_hep = get_db_record('lit', 4328)

    expected = True
    result = _orcid_hep_publication_info_matching(sample_work, sample_hep)

    assert expected == result


def test_get_author_orcids_for_record():
    record = get_db_record('lit', 1496635)

    expected = {
        '0000-0002-7216-5264',
        '0000-0001-7658-8777',
        '0000-0002-0468-541X',
        '0000-0002-8189-8267',
        '0000-0003-4792-9178',
    }
    result = set(_get_author_orcids_for_record(record))

    assert expected == result


def test_push_record_to_all(mock_api):
    record = get_db_record('lit', 1496635)

    push_record_to_all(record)
