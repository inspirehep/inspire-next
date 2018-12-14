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
import time

import pytest
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError, TimeLimitExceeded
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from inspire_dojson.utils import get_record_ref
from inspire_schemas.api import validate
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.orcid.utils import (
    apply_celery_task_with_retry,
    get_literature_recids_for_orcid,
    get_orcids_for_push,
    get_push_access_tokens,
    RetryMixin,
)
from inspirehep.utils.record_getter import get_db_record

from factories.db.invenio_oauthclient import TestRemoteToken


@pytest.fixture(scope='function')
def author_in_isolated_app(isolated_app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/authors.json',
        '_collections': ['Authors'],
        'control_number': 123456789,  # FIXME remove when there is an easy way to insert new records
        'ids': [
            {
                'schema': 'INSPIRE BAI',
                'value': 'J.Smith.1',
            },
            {
                'schema': 'ORCID',
                'value': '0000-0002-1825-0097',
            },
        ],
        'name': {'value': 'Smith, John'},
    }

    assert validate(record, 'authors') is None

    record = InspireRecord.create_or_update(record)
    record.commit()
    yield record['control_number']


def test_orcids_for_push_no_authors(isolated_app):
    record = {
        '_collections': ['Literature'],
        'corporate_author': ['Corporate Author'],
        'document_type': ['article'],
        'titles': [
            {'title': 'A paper with no authors'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == []


def test_orcids_for_push_no_orcids(isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                ],
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == []


def test_orcids_for_push_orcid_in_paper(isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'No Orcid, Jimmy',
            },
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                    {
                        'schema': 'ORCID',
                        'value': '0000-0002-1825-0097',
                    },
                ],
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == ['0000-0002-1825-0097']


def test_orcids_for_push_orcid_in_author_no_claim(author_in_isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'No Orcid, Jimmy',
            },
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                ],
                'record': get_record_ref(author_in_isolated_app, 'authors'),
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == []


def test_orcids_for_push_orcid_in_author_with_claim(author_in_isolated_app):
    record = {
        '_collections': ['Literature'],
        'authors': [
            {
                'full_name': 'No Orcid, Jimmy',
            },
            {
                'full_name': 'Smith, John',
                'ids': [
                    {
                        'schema': 'INSPIRE BAI',
                        'value': 'J.Smith.1',
                    },
                ],
                'record': get_record_ref(author_in_isolated_app, 'authors'),
                'curated_relation': True,
            },
        ],
        'document_type': ['article'],
        'titles': [
            {'title': 'An interesting paper'},
        ],
    }

    assert validate(record, 'hep') is None
    assert list(get_orcids_for_push(record)) == ['0000-0002-1825-0097']


def test_get_literature_recids_for_orcid(isolated_app):
    expected = [1496635]
    result = get_literature_recids_for_orcid('0000-0003-4792-9178')

    assert expected == result


def test_get_literature_recids_for_orcid_raises_if_no_author_is_found(isolated_app):
    with pytest.raises(NoResultFound):
        get_literature_recids_for_orcid('THIS-ORCID-DOES-NOT-EXIST')


def test_get_literature_recids_for_orcid_raises_if_two_authors_are_found(isolated_app):
    record = get_db_record('aut', 1061000)
    record['control_number'] = 1061001
    record = InspireRecord.create_or_update(record)
    record.commit()

    with pytest.raises(MultipleResultsFound):
        get_literature_recids_for_orcid('0000-0003-4792-9178')


def test_get_literature_recids_for_orcid_still_works_if_author_has_no_ids(isolated_app):
    record = get_db_record('aut', 1061000)
    del record['ids']
    record = InspireRecord.create_or_update(record)
    record.commit()

    with pytest.raises(NoResultFound):
        get_literature_recids_for_orcid('0000-0003-4792-9178')


def test_get_literature_recids_for_orcid_still_works_if_author_has_no_orcid_id(isolated_app):
    record = get_db_record('aut', 1061000)
    record['ids'] = [{'schema': 'INSPIRE BAI', 'value': 'Maurizio.Martinelli.1'}]
    record = InspireRecord.create_or_update(record)
    record.commit()

    with pytest.raises(NoResultFound):
        get_literature_recids_for_orcid('0000-0003-4792-9178')


class TestGetPushAccessTokens(object):
    def test_get_push_access_tokens_single_token(self, isolated_app):
        orcid = '0000-0003-4792-9178'
        expected_remote_token = TestRemoteToken.create_for_orcid(orcid).remote_token

        orcids_and_tokens = get_push_access_tokens([orcid])

        assert len(orcids_and_tokens) == 1
        assert orcids_and_tokens[0].id == orcid
        assert orcids_and_tokens[0].access_token == expected_remote_token.access_token

    def test_get_push_access_tokens_multiple_tokens(self, isolated_app):
        orcid1 = '0000-0003-4792-9178'
        expected_remote_token1 = TestRemoteToken.create_for_orcid(orcid1).remote_token
        orcid2 = '0000-0003-4792-9179'
        expected_remote_token2 = TestRemoteToken.create_for_orcid(orcid2).remote_token

        orcids_and_tokens = get_push_access_tokens([orcid1, orcid2])

        assert len(orcids_and_tokens) == 2
        assert orcids_and_tokens[0].id == orcid1
        assert orcids_and_tokens[0].access_token == expected_remote_token1.access_token
        assert orcids_and_tokens[1].id == orcid2
        assert orcids_and_tokens[1].access_token == expected_remote_token2.access_token

    def test_get_push_access_tokens_allow_push(self, isolated_app):
        orcid1 = '0000-0003-4792-9178'
        expected_remote_token = TestRemoteToken.create_for_orcid(orcid1).remote_token
        orcid2 = '0000-0003-4792-9179'
        TestRemoteToken.create_for_orcid(orcid2, allow_push=False).remote_token

        orcids_and_tokens = get_push_access_tokens([orcid1, orcid2])

        assert len(orcids_and_tokens) == 1
        assert orcids_and_tokens[0].id == orcid1
        assert orcids_and_tokens[0].access_token == expected_remote_token.access_token


@shared_task(bind=True)
def get_full_name_test_task(self, first_name, last_name, nick_name='',
                            fail_until_retry_num=0, sleep_time=0,
                            sleep_until_retry_num=0, original_exc=True):
    try:
        # Simulate an exception during the first execution.
        if fail_until_retry_num and self.request.retries < fail_until_retry_num:
            raise AttributeError
        if sleep_time:
            if not sleep_until_retry_num:
                time.sleep(sleep_time)
            if sleep_until_retry_num and self.request.retries < sleep_until_retry_num:
                time.sleep(sleep_time)
    except AttributeError as exc:
        exception = exc
        if not original_exc:
            exception = None
        raise self.retry(max_retries=3, countdown=5, exc=exception)
    return '{} {} {}'.format(first_name, nick_name, last_name)


class TestApplyCeleryTaskWithRetry(object):
    def test_happy_flow(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b')
        with mock.patch('inspirehep.modules.orcid.utils.RetryMixin.retry',
                        wraps=RetryMixin().retry) as mock_retry:
            result = apply_celery_task_with_retry(
                get_full_name_test_task, args=args, kwargs=kwargs)
        assert mock_retry.call_count == 0
        assert result == 'a b c'

    def test_retry(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b', fail_until_retry_num=3)
        with mock.patch('inspirehep.modules.orcid.utils.RetryMixin.retry',
                        wraps=RetryMixin().retry) as mock_retry:
            result = apply_celery_task_with_retry(
                get_full_name_test_task, args=args, kwargs=kwargs, countdown=0,
                max_retries=5)
        assert mock_retry.call_count == 3
        assert result == 'a b c'

    def test_retry_and_fail(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b', fail_until_retry_num=100, original_exc=False)
        with pytest.raises(MaxRetriesExceededError):
            apply_celery_task_with_retry(
                get_full_name_test_task, args=args, kwargs=kwargs, countdown=0,
                max_retries=5)

    def test_retry_and_fail_original_exc(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b', fail_until_retry_num=100)
        with pytest.raises(AttributeError):
            apply_celery_task_with_retry(
                get_full_name_test_task, args=args, kwargs=kwargs, countdown=0,
                max_retries=5)

    def test_countdown_callable(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b', fail_until_retry_num=2)
        backoff = mock.Mock()
        backoff.return_value = 0
        result = apply_celery_task_with_retry(
            get_full_name_test_task, args=args, kwargs=kwargs,
            countdown=backoff, max_retries=5)
        assert backoff.call_count == 2
        assert result == 'a b c'

    def test_time_limit(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b', sleep_time=3)
        with pytest.raises(TimeLimitExceeded):
            apply_celery_task_with_retry(
                get_full_name_test_task, args=args, kwargs=kwargs, countdown=0,
                max_retries=5, time_limit=1)

    def test_time_limit_applied_on_single_attempt(self):
        args = ('a', 'c')
        kwargs = dict(nick_name='b', sleep_time=3, sleep_until_retry_num=3)
        result = apply_celery_task_with_retry(
            get_full_name_test_task, args=args, kwargs=kwargs, countdown=0,
            max_retries=5, time_limit=1)
        assert result == 'a b c'
