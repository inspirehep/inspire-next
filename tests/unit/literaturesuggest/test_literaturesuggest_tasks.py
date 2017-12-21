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

from inspirehep.modules.literaturesuggest.tasks import (
    curation_ticket_context,
    curation_ticket_needed,
    new_ticket_context,
    reply_ticket_context,
)

from mocks import MockEng, MockObj, MockUser


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
    extra_data = {}

    obj = MockObj(data, extra_data)
    user = MockUser('user@example.com')

    expected = {
        'email': 'user@example.com',
        'title': 'foo',
        'identifier': [
            'bar',
        ],
        'user_comment': 'good user comment',
        'object': obj,
        'subject': 'Your suggestion to INSPIRE: foo',
    }
    result = new_ticket_context(user, obj)

    assert expected == result


def test_new_ticket_context_handles_unicode():
    data = {
        'titles': [
            {
                'title': (
                    u'Chocs caractéristiques et ondes simples '
                    u'exceptionnelles pour les systèmes conservatifs à '
                    u"intégrale d'énergie: forme explicite de la solution"
                ),
            },
        ],
    }
    extra_data = {}

    obj = MockObj(data, extra_data)
    user = MockUser('user@example.com')

    expected = {
        'email': 'user@example.com',
        'title': (
            u'Chocs caractéristiques et ondes simples exceptionnelles pour '
            u"les systèmes conservatifs à intégrale d'énergie: forme "
            u'explicite de la solution'
        ),
        'identifier': '',
        'user_comment': '',
        'object': obj,
        'subject': (
            u'Your suggestion to INSPIRE: Chocs caractéristiques et ondes '
            u'simples exceptionnelles pour les systèmes conservatifs à '
            u"intégrale d'énergie: forme explicite de la solution"
        ),
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

    obj = MockObj(data, extra_data)
    user = MockUser('user@example.com')

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
    extra_data = {
        'recid': 'baz',
        'url': 'qux',
        'submission_pdf': 'http://path.to/my.pdf',
    }

    obj = MockObj(data, extra_data)
    user = MockUser('user@example.com')

    expected = {
        'recid': 'baz',
        'record_url': 'qux',
        'link_to_pdf': 'http://path.to/my.pdf',
        'email': 'user@example.com',
        'user_comment': 'good user comment',
        'subject': 'math.GT/0309136 arXiv:0706.0001v1 doi:bar foo (#baz)',
    }
    result = curation_ticket_context(user, obj)

    assert expected == result


def test_curation_ticket_needed():
    obj = MockObj({}, {'core': True})
    eng = MockEng()

    assert curation_ticket_needed(obj, eng)
