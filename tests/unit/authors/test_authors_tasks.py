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

import pytest
from flask import current_app
from mock import patch

from invenio_accounts.models import User

from inspirehep.modules.authors.tasks import (
    new_ticket_context,
    update_ticket_context,
    reply_ticket_context,
    curation_ticket_context
)

from mocks import MockObj


@pytest.fixture()
def data():
    return {
        'control_number': 123,
        'name': {
            'preferred_name': 'John Doe'
        },
        'bai': 'John.Doe.1',
        '_private_notes': [
            {
                'value': 'not user comment',
                'source': 'arxiv',
            },
            {
                'value': 'good user comment',
                'source': 'submitter',
            },
        ],
    }


@pytest.fixture()
def unicode_data():
    return {
        'bai': 'Diego.Martinez.Santos.1',
        'control_number': 123,
        'name': {
            'preferred_name': u'Diego Martínez',
        },
        '_private_notes': [
            {
                'value': 'not user comment',
                'source': 'arxiv',
            },
            {
                'value': u'good user comment from user Diego Martínez',
                'source': 'submitter',
            },
        ],
    }


@pytest.fixture()
def extra_data():
    return {
        'reason': 'Test reason',
        'url': 'http://example.com',
        'recid': 123,
    }


@pytest.fixture()
def user():
    return User(email="foo@bar.com")


def test_new_ticket_context(data, extra_data, user):
    obj = MockObj(data, extra_data)
    ctx = new_ticket_context(user, obj)

    assert isinstance(ctx['object'], MockObj)
    assert ctx['email'] == 'foo@bar.com'
    assert ctx['subject'] == 'Your suggestion to INSPIRE: author John Doe'
    assert ctx['user_comment'] == 'good user comment'


def test_new_ticket_context_handles_unicode(unicode_data, extra_data, user):
    obj = MockObj(unicode_data, extra_data)
    ctx = new_ticket_context(user, obj)

    assert isinstance(ctx['object'], MockObj)
    assert ctx['email'] == 'foo@bar.com'
    assert ctx['subject'] == u'Your suggestion to INSPIRE: author Diego Martínez'
    assert ctx['user_comment'] == u'good user comment from user Diego Martínez'


def test_update_ticket_context(data, extra_data, user):
    config = {
        'AUTHORS_UPDATE_BASE_URL': 'http://inspirehep.net'
    }
    obj = MockObj(data, extra_data)
    with patch.dict(current_app.config, config):
        expected = {
            'url': 'http://inspirehep.net/record/123',
            'bibedit_url': 'http://inspirehep.net/record/123/edit',
            'email': 'foo@bar.com',
            'user_comment': 'good user comment',
            'subject': 'Your update to author John Doe on INSPIRE',
        }
        ctx = update_ticket_context(user, obj)
        assert ctx == expected


def test_update_ticket_context_handles_unicode(unicode_data, extra_data, user):
    config = {
        'AUTHORS_UPDATE_BASE_URL': 'http://inspirehep.net'
    }
    obj = MockObj(unicode_data, extra_data)
    with patch.dict(current_app.config, config):
        expected = {
            'url': 'http://inspirehep.net/record/123',
            'bibedit_url': 'http://inspirehep.net/record/123/edit',
            'email': 'foo@bar.com',
            'user_comment': u'good user comment from user Diego Martínez',
            'subject': u'Your update to author Diego Martínez on INSPIRE',
        }
        ctx = update_ticket_context(user, obj)
        assert ctx == expected


def test_reply_ticket_context(data, extra_data, user):
    obj = MockObj(data, extra_data)
    ctx = reply_ticket_context(user, obj)
    assert isinstance(ctx['object'], MockObj)
    assert isinstance(ctx['user'], User)
    assert ctx['author_name'] == 'John Doe'
    assert ctx['reason'] == 'Test reason'
    assert ctx['record_url'] == 'http://example.com'


def test_curation_ticket_context(data, extra_data, user):
    obj = MockObj(data, extra_data)
    ctx = curation_ticket_context(user, obj)
    assert isinstance(ctx['object'], MockObj)
    assert ctx['recid'] == 123
    assert ctx['user_comment'] == 'good user comment'
    assert ctx['subject'] == 'Curation needed for author John Doe [John.Doe.1]'
    assert ctx['email'] == 'foo@bar.com'
    assert ctx['record_url'] == 'http://example.com'


def test_curation_ticket_context_handles_unicode(unicode_data, extra_data, user):
    obj = MockObj(unicode_data, extra_data)
    ctx = curation_ticket_context(user, obj)
    assert isinstance(ctx['object'], MockObj)
    assert ctx['user_comment'] == u'good user comment from user Diego Martínez'
    assert ctx['subject'] == u'Curation needed for author Diego Martínez [Diego.Martinez.Santos.1]'
    assert ctx['email'] == 'foo@bar.com'
    assert ctx['record_url'] == 'http://example.com'
