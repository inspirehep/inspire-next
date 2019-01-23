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

from __future__ import absolute_import, division, print_function

import os

import pkg_resources
import pytest
import mock

from elasticsearch import NotFoundError

from inspire_schemas.readers import LiteratureReader
from invenio_db import db
from invenio_oauthclient.utils import oauth_link_external_id
from invenio_oauthclient.models import (
    RemoteAccount,
    RemoteToken,
    User,
    UserIdentity,
)
from invenio_search import current_search_client as es
from invenio_records.signals import after_record_update

from inspirehep.modules.migrator.tasks import migrate_and_insert_record
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.records.errors import MissingInspireRecordError, MissingCitedRecordError
from inspirehep.modules.records.tasks import index_modified_citations_from_record
from inspirehep.modules.search import LiteratureSearch
from inspirehep.utils.record_getter import get_es_record, RecordGetterError, get_db_record


from utils import _delete_record, override_config
from factories.db.invenio_records import TestRecordMetadata


@pytest.fixture(scope='function')
def user_with_permission(app):
    _user_data = {
        'orcid': '0000-0001-8829-5461',
        'token': '3d25a708-dae9-48eb-b676-aaaaaaaaaaaa',
        'email': 'dummy1@email.com',
        'name': 'Franz Kärtner',
        'consumer_key': '0000-0000-0000-0000',
        'allow_push': True,
    }

    create_user(**_user_data)

    yield _user_data

    cleanup_user_record(_user_data)


@pytest.fixture(scope='function')
def two_users_with_permission(app):
    _user1_data = {
        'orcid': '0000-0001-8829-5461',
        'token': '3d25a708-dae9-48eb-b676-aaaaaaaaaaaa',
        'email': 'dummy1@email.com',
        'name': 'Franz Kärtner',
        'consumer_key': '0000-0000-0000-0000',
        'allow_push': True,
    }
    _user2_data = {
        'orcid': '0000-0002-2174-4493',
        'token': '3d25a708-dae9-48eb-b676-bbbbbbbbbbbb',
        'email': 'dummy2@email.com',
        'name': 'Kranz Färtner Son',
        'consumer_key': '0000-0000-0000-0000',
        'allow_push': True,
    }

    create_user(**_user1_data)
    create_user(**_user2_data)

    yield _user1_data, _user2_data

    cleanup_user_record(_user1_data)
    cleanup_user_record(_user2_data)


@pytest.fixture(scope='function')
def user_without_permission(app):
    _user_data = {
        'orcid': '0000-0001-8829-5461',
        'token': '3d25a708-dae9-48eb-b676-aaaaaaaaaaaa',
        'email': 'dummy1@email.com',
        'name': 'Franz Kärtner',
        'consumer_key': '0000-0000-0000-0000',
        'allow_push': False,
    }

    create_user(**_user_data)

    yield _user_data

    cleanup_user_record(_user_data)


@pytest.fixture(scope='function')
def user_without_token(app):
    _user_data = {
        'orcid': '0000-0001-8829-5461',
        'email': 'dummy1@email.com',
        'name': 'Franz Kärtner',
        'consumer_key': '0000-0000-0000-0000',
        'allow_push': False,
    }

    create_user(**_user_data)

    yield _user_data

    cleanup_user_record(_user_data)


@pytest.fixture(scope='function')
def raw_record(app):
    record_fixture_path = pkg_resources.resource_filename(
        __name__,
        os.path.join('fixtures', '1608652.xml')
    )

    with open(record_fixture_path) as _record_fixture_fd:
        yield _record_fixture_fd.read()

    _delete_record('lit', 1608652)


@pytest.fixture(scope='function')
def record(raw_record):
    with mock.patch('inspirehep.modules.orcid.tasks.orcid_push') as mock_orcid_push:
        mock_orcid_push.return_value = mock_orcid_push
        _record = migrate_and_insert_record(raw_record, skip_files=True)

    return _record


@pytest.fixture
def enable_orcid_push_feature(app):
    with mock.patch.dict(app.config, {'FEATURE_FLAG_ENABLE_ORCID_PUSH': True}):
        yield


def create_user(orcid, email, name, consumer_key, token=None, allow_push=False):
    user = User()
    user.email = email
    with db.session.begin_nested():
        db.session.add(user)

    oauth_link_external_id(user, {
        'id': orcid,
        'method': 'orcid'
    })

    if token:
        with db.session.begin_nested():
            db.session.add(
                RemoteToken.create(
                    user_id=user.id,
                    client_id=consumer_key,
                    token=token,
                    secret=None,
                    extra_data={
                        'orcid': orcid,
                        'full_name': name,
                        'allow_push': allow_push,
                    }
                )
            )


def assert_db_has_no_user_record(user_record):
    assert User.query.filter_by(email=user_record['email']).count() == 0
    assert RemoteAccount.query.join(User).join(UserIdentity).filter(UserIdentity.id == user_record['orcid']).count() == 0
    if 'token' in user_record:
        assert RemoteToken.query.filter_by(access_token=user_record['token']).count() == 0

    assert UserIdentity.query.filter_by(id=user_record['orcid']).count() == 0


def cleanup_user_record(user_record):
    if 'token' in user_record:
        RemoteToken.query.filter_by(access_token=user_record['token']).delete()
    user_id = db.session.query(UserIdentity.id_user).filter(UserIdentity.id == user_record['orcid']).subquery()
    RemoteAccount.query.filter(RemoteAccount.user_id.in_(user_id)).delete(synchronize_session='fetch')
    UserIdentity.query.filter_by(id=user_record['orcid']).delete()
    User.query.filter_by(email=user_record['email']).delete()
    assert_db_has_no_user_record(user_record)


def assert_db_has_no_author_record(author_recid):
    assert InspireRecord.query.filter_by().count() == 0


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_not_trigger_for_author_records(mock_orcid_push_task, user_with_permission):
    mock_orcid_push_task.assert_not_called()


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_not_triggered_on_create_record_without_allow_push(mock_orcid_push_task, app, raw_record, user_without_permission):
    migrate_and_insert_record(raw_record, skip_files=True)

    mock_orcid_push_task.assert_not_called()


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_not_triggered_on_create_record_without_token(mock_orcid_push_task, app, raw_record, user_without_token):
    migrate_and_insert_record(raw_record, skip_files=True)

    mock_orcid_push_task.assert_not_called()


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_triggered_on_create_record_with_allow_push(mock_orcid_push_task, app, raw_record, user_with_permission, enable_orcid_push_feature):
    migrate_and_insert_record(raw_record, skip_files=True)

    expected_kwargs = {
        'kwargs': {
            'orcid': user_with_permission['orcid'],
            'rec_id': 1608652,
            'oauth_token': user_with_permission['token'],
            'kwargs_to_pusher': {'record_db_version': mock.ANY},
        },
        'queue': 'orcid_push',
    }

    mock_orcid_push_task.apply_async.assert_called_once_with(**expected_kwargs)


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_triggered_on_record_update_with_allow_push(mock_orcid_push_task, app, record, user_with_permission, enable_orcid_push_feature):
    expected_kwargs = {
        'kwargs': {
            'orcid': user_with_permission['orcid'],
            'rec_id': 1608652,
            'oauth_token': user_with_permission['token'],
            'kwargs_to_pusher': {'record_db_version': mock.ANY},
        },
        'queue': 'orcid_push',
    }

    record.commit()

    mock_orcid_push_task.apply_async.assert_called_once_with(**expected_kwargs)


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_triggered_on_create_record_with_multiple_authors_with_allow_push(mock_orcid_push_task, app, raw_record, two_users_with_permission, enable_orcid_push_feature):
    migrate_and_insert_record(raw_record, skip_files=True)

    expected_kwargs_user1 = {
        'kwargs': {
            'orcid': two_users_with_permission[0]['orcid'],
            'rec_id': 1608652,
            'oauth_token': two_users_with_permission[0]['token'],
            'kwargs_to_pusher': {'record_db_version': mock.ANY},
        },
        'queue': 'orcid_push',
    }
    expected_kwargs_user2 = {
        'kwargs': {
            'orcid': two_users_with_permission[1]['orcid'],
            'rec_id': 1608652,
            'oauth_token': two_users_with_permission[1]['token'],
            'kwargs_to_pusher': {'record_db_version': mock.ANY},
        },
        'queue': 'orcid_push',
    }

    mock_orcid_push_task.apply_async.assert_any_call(**expected_kwargs_user1)
    mock_orcid_push_task.apply_async.assert_any_call(**expected_kwargs_user2)
    assert mock_orcid_push_task.apply_async.call_count == 2


def test_creating_deleted_record_and_undeleting_created_record_in_es(app):
    search = LiteratureSearch()
    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        'deleted': True,
        '_collections': ['Literature']
    }

    # When a record is created in the DB with deleted flag True, it is not created in ES.

    record = InspireRecord.create(json)
    record.commit()
    db.session.commit()
    with pytest.raises(NotFoundError):
        search.get_source(record.id)

    # When a record is undeleted, it is created in ES.
    record['deleted'] = False
    record.commit()
    db.session.commit()
    search.get_source(record.id)
    record._delete(force=True)


def test_that_db_changes_are_mirrored_in_es(app):
    search = LiteratureSearch()
    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': ['Literature']
    }

    # When a record is created in the DB, it is also created in ES.

    record = InspireRecord.create(json)
    record.commit()
    db.session.commit()
    es_record = search.get_source(record.id)

    assert LiteratureReader(es_record).title == 'foo'

    # When a record is updated in the DB, is is also updated in ES.

    record['titles'][0]['title'] = 'bar'
    record.commit()
    db.session.commit()
    es_record = search.get_source(record.id)

    assert LiteratureReader(es_record).title == 'bar'

    # When a record is deleted in the DB, it is also deleted in ES.

    record._delete(force=True)
    db.session.commit()

    with pytest.raises(NotFoundError):
        es_record = search.get_source(record.id)


def test_deleting_record_triggers_delete_in_es(app):
    search = LiteratureSearch()
    json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'foo'},
        ],
        '_collections': ['Literature']
    }

    # When a record is created in the DB, it is also created in ES.

    record = InspireRecord.create(json)
    record.commit()
    db.session.commit()
    search.get_source(record.id)

    # When a record is updated with deleted flag true, it is deleted in ES
    record['deleted'] = True
    record.commit()
    db.session.commit()
    with pytest.raises(NotFoundError):
        search.get_source(record.id)


@mock.patch('inspirehep.modules.orcid.tasks.orcid_push')
def test_orcid_push_not_triggered_on_create_record_no_feat_flag(mocked_Task, app, raw_record, user_with_permission):
    migrate_and_insert_record(raw_record, skip_files=True)

    mocked_Task.assert_not_called()


def test_check_enhance_after_index_receiver_when_sender_is_not_a_record(isolated_app):
    json_rec = {
        "titles": [
            {
                "title": "Some title"
            },
        ],
        "$schema": "https://qa.inspirehep.net/schemas/records/hep.json",
        "authors": [
            {
                "uuid": "e4110d73-5f9e-46a5-b7d8-668d727a3acf",
                "full_name": "Raczka, P.A.",
            }
        ],
        "citeable": True,
        "abstracts": [
            {
                "value": "Abstract value"
            }
        ],
        "control_number": 425592,
    }
    record = TestRecordMetadata.create_from_kwargs(json=json_rec).inspire_record
    after_record_update.send(
        isolated_app,
        record=record
    )

    assert 'citation_count' in record.model._enhanced_record


def test_check_enhance_after_index_receiver_when_record_not_provided(isolated_app):
    json_rec = {
        "titles": [
            {
                "title": "Some title"
            },
        ],
        "$schema": "https://qa.inspirehep.net/schemas/records/hep.json",
        "authors": [
            {
                "uuid": "e4110d73-5f9e-46a5-b7d8-668d727a3acf",
                "full_name": "Raczka, P.A.",
            }
        ],
        "citeable": True,
        "abstracts": [
            {
                "value": "Abstract value"
            }
        ],
        "control_number": 425592,
    }
    with pytest.raises(MissingInspireRecordError) as exc:
        after_record_update.send(
            isolated_app,
            json=json_rec,
            record=None
        )
    assert str(exc.value) == "Record is not InspireRecord!"


@mock.patch(
    'inspirehep.modules.records.wrappers.has_update_permission',
    return_value=True
)
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.delay')
def test_index_after_commit_indexes_also_cites_record_when_new_citation_is_added(
    mocked_indexing_task,
    mocked_permission_check,
    app,
):
    # this test doesn't use the isolated_app because it needs to commit to
    # the DB in order to create records versions.
    json_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'This is the record being cited'}],
        'control_number': 9999,
        '_collections': ['Literature']
    }
    cited = InspireRecord.create(data=json_data, skip_files=True)
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = 'lit', cited['control_number'], 1
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    citing_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Record citing the first one'}],
        '_collections': ['Literature'],
        'control_number': 8888,
        'references': [
            {"reference": {'authors': [{'full_name': 'Smith, J.'}]}}
        ]
    }

    record = InspireRecord.create(data=citing_json, skip_files=True)
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = 'lit', record['control_number'], 1
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    references = {
        'references': [
            {
                "curated_relation": False,
                "record": {
                    "$ref": "http://localhost:5000/api/literature/9999"
                },
                "reference": {
                    'authors': [{'full_name': 'Smith, J.'}],
                }
            }
        ]
    }

    citing_json.update(references)
    record.clear()
    record.update(citing_json)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = 'lit', record['control_number'], 2
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 1
    assert LiteratureSearch.citations(es_rec).total == 1

    _delete_record('lit', 8888)
    _delete_record('lit', 9999)


@mock.patch(
    'inspirehep.modules.records.wrappers.has_update_permission',
    return_value=True
)
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.delay')
def test_index_after_commit_indexes_also_cites_record_when_citation_is_deleted(
    mocked_indexing_task,
    mocked_permission_check,
    app,
):
    # this test doesn't use the isolated_app because it needs to commit to
    # the DB in order to create records versions.
    json_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'This is the record being cited'}],
        'control_number': 9999,
        '_collections': ['Literature']
    }

    cited = InspireRecord.create(data=json_data, skip_files=True)
    cited.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', cited['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    citing_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Record citing the first one'}],
        '_collections': ['Literature'],
        'control_number': 8888,
        'references': [
            {
                'record': {
                    '$ref': 'http://localhost:5000/api/literature/9999'
                },
                'reference': {
                    'authors': [{'full_name': 'Smith, J.'}],
                }
            }
        ]
    }

    record = InspireRecord.create(data=citing_json, skip_files=True)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 1
    assert LiteratureSearch.citations(es_rec).total == 1

    del citing_json['references']
    record.clear()
    record.update(citing_json)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 3)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    _delete_record('lit', record['control_number'])
    _delete_record('lit', cited['control_number'])


@mock.patch(
    'inspirehep.modules.records.wrappers.has_update_permission',
    return_value=True
)
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.delay')
def test_index_after_commit_indexes_also_cites_two_records(
    mocked_indexing_task,
    mocked_permission_check,
    app,
):
    # this test doesn't use the isolated_app because it needs to commit to
    # the DB in order to create records versions.
    json1 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'This is the record being cited'}],
        'control_number': 9999,
        '_collections': ['Literature']
    }

    cited1 = InspireRecord.create(data=json1, skip_files=True)
    cited1.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', cited1['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    json2 = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'This also is the record being cited'}],
        'control_number': 9998,
        '_collections': ['Literature']
    }

    cited2 = InspireRecord.create(data=json2, skip_files=True)
    cited2.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', cited2['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec1 = get_es_record('lit', 9999)
    es_rec2 = get_es_record('lit', 9998)
    assert es_rec1['citation_count'] == 0
    assert es_rec2['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec1).total == 0
    assert LiteratureSearch.citations(es_rec2).total == 0

    citing_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Record citing the first one'}],
        '_collections': ['Literature'],
        'control_number': 8888,
        'references': [
            {
                'reference': {
                    'authors': [{'full_name': 'Smith, J.'}],
                }
            }
        ]
    }

    record = InspireRecord.create(data=citing_json, skip_files=True)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec1 = get_es_record('lit', 9999)
    es_rec2 = get_es_record('lit', 9998)
    assert es_rec1['citation_count'] == 0
    assert es_rec2['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec1).total == 0
    assert LiteratureSearch.citations(es_rec2).total == 0

    references = {
        'references': [
            {
                'record': {
                    '$ref': 'http://localhost:5000/api/literature/9998'
                },
            },
            {
                'record': {
                    '$ref': 'http://localhost:5000/api/literature/9999'
                },
            }
        ]
    }

    citing_json.update(references)
    record.clear()
    record.update(citing_json)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 3)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec1 = get_es_record('lit', 9999)
    es_rec2 = get_es_record('lit', 9998)
    assert es_rec1['citation_count'] == 1
    assert es_rec2['citation_count'] == 1
    assert LiteratureSearch.citations(es_rec1).total == 1
    assert LiteratureSearch.citations(es_rec2).total == 1

    _delete_record('lit', record['control_number'])
    _delete_record('lit', cited1['control_number'])
    _delete_record('lit', cited2['control_number'])


@mock.patch(
    'inspirehep.modules.records.wrappers.has_update_permission',
    return_value=True
)
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.delay')
def test_index_after_commit_indexes_also_cites_record_when_citer_is_deleted(
    mocked_indexing_task,
    mocked_permission_check,
    app,
):
    # this test doesn't use the isolated_app because it needs to commit to
    # the DB in order to create records versions.

    json_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'This is the record being cited'}],
        'control_number': 9999,
        '_collections': ['Literature']
    }

    cited = InspireRecord.create(data=json_data, skip_files=True)
    cited.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', 9999, 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    citing_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Record citing the first one'}],
        '_collections': ['Literature'],
        'control_number': 8888,
        'references': [
            {
                'record': {
                    '$ref': 'http://localhost:5000/api/literature/9999'
                },
                'reference': {
                    'authors': [{'full_name': 'Smith, J.'}],
                }
            }
        ]
    }

    record = InspireRecord.create(data=citing_json, skip_files=True)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 1
    assert LiteratureSearch.citations(es_rec).total == 1

    record.delete()
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 3)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    _delete_record('lit', record['control_number'])
    _delete_record('lit', cited['control_number'])


@mock.patch(
    'inspirehep.modules.records.wrappers.has_update_permission',
    return_value=True
)
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.delay')
def test_regression_index_after_commit_retries_for_new_record_not_yet_in_db(
    mocked_indexing_task,
    mocked_permission_check,
    app,
):
    # this test doesn't use the isolated_app because it needs to commit to
    # the DB in order to create records versions.

    json_data = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'This is the record being cited'}],
        'control_number': 9999,
        '_collections': ['Literature']
    }

    cited = InspireRecord.create(data=json_data, skip_files=True)
    cited.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', 9999, 2)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    es_rec = get_es_record('lit', 9999)
    assert es_rec['citation_count'] == 0
    assert LiteratureSearch.citations(es_rec).total == 0

    citing_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Record citing the first one'}],
        '_collections': ['Literature'],
        'control_number': 8888,
        'references': [
            {
                'record': {
                    '$ref': 'http://localhost:5000/api/literature/9999'
                },
                'reference': {
                    'authors': [{'full_name': 'Smith, J.'}],
                }
            }
        ]
    }

    record = InspireRecord.create(data=citing_json, skip_files=True)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 2)
    mocked_indexing_task.assert_called_with(*expected_args)

    # execute mocked task pretending record is not committed yet to DB
    _delete_record('lit', record['control_number'])
    with pytest.raises(RecordGetterError):
        # XXX: celery in eager mode does not retry, so it raises the first time
        index_modified_citations_from_record(*expected_args)

    _delete_record('lit', cited['control_number'])


@mock.patch(
    'inspirehep.modules.records.wrappers.has_update_permission',
    return_value=True
)
@mock.patch('inspirehep.modules.records.receivers.index_modified_citations_from_record.delay')
def test_index_after_commit_indexes_raises_if_cited_records_are_not_in_db(
    mocked_indexing_task,
    mocked_permission_check,
    app,
):
    # this test doesn't use the isolated_app because it needs to commit to
    # the DB in order to create records versions.

    citing_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': ['article'],
        'titles': [{'title': 'Record citing the first one'}],
        '_collections': ['Literature'],
        'control_number': 8888,
        'references': [
            {"reference": {'authors': [{'full_name': 'Smith, J.'}]}}
        ]
    }

    record = InspireRecord.create(data=citing_json, skip_files=True)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = 'lit', record['control_number'], 2
    mocked_indexing_task.assert_called_with(*expected_args)

    # execute mocked task
    index_modified_citations_from_record(*expected_args)

    references = {
        'references': [
            {
                "curated_relation": False,
                "record": {
                    "$ref": "http://localhost:5000/api/literature/9999"
                },
                "reference": {
                    'authors': [{'full_name': 'Smith, J.'}],
                }
            }
        ]
    }

    citing_json.update(references)
    record.clear()
    record.update(citing_json)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')

    expected_args = ('lit', record['control_number'], 3)
    mocked_indexing_task.assert_called_with(*expected_args)
    # execute mocked task
    with pytest.raises(MissingCitedRecordError):
        index_modified_citations_from_record(*expected_args)

    _delete_record('lit', 8888)


def test_record_enhanced_in_es_and_not_enhanced_in_db(app):
    record_json = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'document_type': [
            'article',
        ],
        'control_number': 111,
        'titles': [
            {
                'title': 'Jessica Jones',
            },
        ],
        '_collections': ['Literature'],
        'references': [{'record': {'$ref': 'http://localhost:5000/api/literature/1498589'}}]
    }
    record = InspireRecord.create(record_json)
    record.commit()
    db.session.commit()
    es.indices.refresh('records-hep')
    rec1 = get_db_record('lit', 111)
    rec2 = get_es_record('lit', 111)
    assert 'facet_author_name' not in rec1
    assert 'facet_author_name' in rec2
    _delete_record('lit', 111)


@pytest.mark.usefixtures('isolated_app')
class TestPushToOrcid(object):
    def test_existing_record(self):
        recid = 736770
        inspire_record = get_db_record('lit', recid)  # from demosite data.
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*',
                             ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}), \
                mock.patch('inspirehep.modules.records.receivers.push_access_tokens') as mock_push_access_tokens, \
                mock.patch('inspirehep.modules.orcid.tasks.orcid_push.apply_async') as mock_apply_async:
            mock_push_access_tokens.get_access_tokens.return_value = [('myorcid', 'mytoken')]
            inspire_record.commit()
            mock_apply_async.assert_called_once_with(
                kwargs={'orcid': 'myorcid',
                        'oauth_token': 'mytoken',
                        'kwargs_to_pusher': {'record_db_version': inspire_record.model.version_id},
                        'rec_id': recid},
                queue='orcid_push')

    def test_new_record(self):
        recid = 9999912587
        record_json = {
            '$schema': 'http://localhost:5000/schemas/records/hep.json',
            'document_type': [
                'article',
            ],
            'control_number': recid,
            'titles': [
                {
                    'title': 'Jessica Jones',
                },
            ],
            '_collections': ['Literature'],
            'references': [{'record': {
                '$ref': 'http://localhost:5000/api/literature/1498589'}}]
        }
        inspire_record = InspireRecord.create(record_json)
        with override_config(FEATURE_FLAG_ENABLE_ORCID_PUSH=True,
                             FEATURE_FLAG_ORCID_PUSH_WHITELIST_REGEX='.*',
                             ORCID_APP_CREDENTIALS={'consumer_key': '0000-0001-8607-8906'}), \
                mock.patch('inspirehep.modules.records.receivers.push_access_tokens') as mock_push_access_tokens, \
                mock.patch('inspirehep.modules.orcid.tasks.orcid_push.apply_async') as mock_apply_async:
            mock_push_access_tokens.get_access_tokens.return_value = [('myorcid', 'mytoken')]
            inspire_record.commit()
            mock_apply_async.assert_called_once_with(
                kwargs={'orcid': 'myorcid',
                        'oauth_token': 'mytoken',
                        'kwargs_to_pusher': {'record_db_version': inspire_record.model.version_id},
                        'rec_id': recid},
                queue='orcid_push')
        _delete_record('lit', recid)
