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

import mock
import pytest

from inspirehep.modules.literaturesuggest.tasks import (
    new_ticket_context,
    reply_ticket_context,
    curation_ticket_context,
    curation_ticket_needed,
    formdata_to_model,
)


class StubObj(object):
    def __init__(self, data, extra_data, id=1, id_user=1):
        self.data = data
        self.extra_data = extra_data
        self.id = id
        self.id_user = id_user


class DummyEng(object):
    pass


class StubUser(object):
    def __init__(self, email):
        self.email = email


@pytest.mark.parametrize(
    'expected_result,formdata',
    [
        (
            True,
            {
                'journal_title': 'High Energy Physics Libraries Webzine',
                'volume': '192',
                'year': '2011',
                'page_range_article_id': '2550'
            }
        ), (
            None,
            {
                'journal_title': 'High Energy Physics Libraries Webzine',
                'volume': '192',
                'year': '2011',
            }
        ), (
            None,
            {
                'journal_title': 'High Energy Physics Libraries Webzine',
                'year': '2011',
                'page_range_article_id': '2550'
            }
        )
    ]
)
@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.normalize_journal_title')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.LiteratureBuilder.validate_record')
def test_formdata_to_model_is_not_citeable(
    mock_validate_record,
    mock_normalize_journal_title,
    user_identity,
    user,
    expected_result,
    formdata,
):
    mock_validate_record.return_value = None
    mock_normalize_journal_title.return_value = formdata['journal_title']

    data = {}
    extra_data = {}
    obj = StubObj(data, extra_data)

    result = formdata_to_model(obj, formdata)
    assert result.get('citeable') is expected_result


def test_new_ticket_context():
    data = {
        'titles': [
            {
                'title': 'foo',
            },
        ],
        'external_system_numbers': [
            {
                'value': 'bar',
            },
        ],
    }
    extra_data = {
        'formdata': {
            'extra_comments': [
                'baz',
            ],
            'references': [
                'qux',
            ],
        },
    }

    obj = StubObj(data, extra_data)
    user = StubUser('user@example.com')

    expected = {
        'email': 'user@example.com',
        'title': 'foo',
        'identifier': [
            'bar',
        ],
        'user_comment': [
            'baz',
        ],
        'references': [
            'qux',
        ],
        'object': obj,
        'subject': 'Your suggestion to INSPIRE: foo',
    }
    result = new_ticket_context(user, obj)

    assert expected == result


def test_reply_ticket_context():
    data = {
        'titles': [
            {
                'title': 'foo',
            },
        ],
    }
    extra_data = {
        'reason': 'bar',
        'url': 'baz',
    }

    obj = StubObj(data, extra_data)
    user = StubUser('user@example.com')

    expected = {
        'object': obj,
        'user': user,
        'title': 'foo',
        'reason': 'bar',
        'record_url': 'baz',
    }
    result = reply_ticket_context(user, obj)

    assert expected == result


def test_curation_ticket_context():
    data = {
        'arxiv_eprints': [
            {
                'value': 'math.GT/0309136',
            },
            {
                'value': '0706.0001v1',
            },
        ],
        'report_numbers': [
            {
                'value': 'foo',
            },
        ],
        'dois': [
            {
                'value': 'bar',
            },
        ],
    }
    extra_data = {
        'recid': 'baz',
        'url': 'qux',
        'formdata': {
            'url': 'quux',
            'references': [
                'plugh',
            ],
            'extra_comments': [
                'xyzzy',
            ]
        }
    }

    obj = StubObj(data, extra_data)
    user = StubUser('user@example.com')

    expected = {
        'recid': 'baz',
        'record_url': 'qux',
        'link_to_pdf': 'quux',
        'email': 'user@example.com',
        'references': [
            'plugh',
        ],
        'user_comment': [
            'xyzzy',
        ],
        'subject': 'math.GT/0309136 arXiv:0706.0001v1 doi:bar foo (#baz)',
    }
    result = curation_ticket_context(user, obj)

    assert expected == result


def test_curation_ticket_needed():
    obj = StubObj({}, {'core': True})
    eng = DummyEng()

    assert curation_ticket_needed(obj, eng)
