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

from __future__ import absolute_import, division, print_function

import mock
import pytest
from elasticsearch_dsl.result import Response

from inspirehep.modules.literaturesuggest.tasks import (
    formdata_to_model,
    new_ticket_context,
    reply_ticket_context,
    curation_ticket_context,
    curation_ticket_needed,
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


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_schema(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
    }

    obj = StubObj(data, extra_data)

    expected = 'https://localhost:5000/schemas/records/hep.json'
    result = formdata_to_model(obj, formdata)

    assert expected == result['$schema']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_collections_from_type_of_doc_thesis(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'thesis',
        'title': [
            'foo',
        ],
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'primary': 'HEP',
        },
        {
            'primary': 'THESIS',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['collections']
    assert obj.data == {}


@pytest.mark.xfail(reason='missing spec')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_collections_from_inspire_categories_if_arxiv(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'categories': 'baz',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'primary': 'HEP',
        },
        {
            'primary': 'arXiv',
        },
        {
            'primary': 'Citeable',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['collections']
    assert obj.data == {}


@pytest.mark.xfail(reason='missing spec')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_abstracts_from_abstracts_if_arxiv(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'categories': 'baz',
        'abstract': ' qux ',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'source': 'arXiv',
            'value': 'qux',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['abstracts']
    assert obj.data == {}


@pytest.mark.xfail(reason='missing spec')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_external_system_numbers_from_arxiv_id(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'arxiv_id': 'baz',
        'categories': 'foo',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'value': 'oai:arXiv.org:baz',
            'institute': 'arXiv',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['external_system_numbers']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_collections_from_complete_publication_info(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'issue': 'baz',
        'volume': 'qux',
        'year': 'quux',
        'page_range_article_id': '25-50'
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'primary': 'HEP',
        },
        {
            'primary': 'Published',
        },
        {
            'primary': 'Citeable',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['collections']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_titles_from_title_arXiv(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'title_arXiv': 'baz',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'source': 'submitter',
            'title': 'bar',
        },
        {
            'source': 'arXiv',
            'title': 'baz',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['titles']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_titles_from_title_crossref(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'title_crossref': 'baz',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'source': 'submitter',
            'title': 'bar',
        },
        {
            'source': 'CrossRef',
            'title': 'baz',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['titles']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_collections_and_hidden_notes_from_conf_name(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'conf_name': 'baz',
    }

    obj = StubObj(data, extra_data)

    result = formdata_to_model(obj, formdata)

    assert result['collections'] == [
        {
            'primary': 'HEP',
        },
        {
            'primary': 'ConferencePaper',
        },
    ]
    assert result['hidden_notes'] == [
        {
            'value': 'baz',
        },
    ]
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_collections_and_hidden_notes_from_conf_name_and_nonpublic_note(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'conf_name': 'baz',
        'nonpublic_note': 'qux',
    }

    obj = StubObj(data, extra_data)

    result = formdata_to_model(obj, formdata)

    assert result['collections'] == [
        {
            'primary': 'HEP',
        },
        {
            'primary': 'ConferencePaper',
        },
    ]
    assert result['hidden_notes'] == [
        {
            'value': 'baz',
        },
        {
            'value': 'qux',
        },
    ]
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_number_of_pages_from_page_range_article_id(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'page_range_article_id': '1-10',
    }

    obj = StubObj(data, extra_data)

    expected = 10
    result = formdata_to_model(obj, formdata)

    assert expected == result['number_of_pages']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_no_number_of_pages_when_invalid_page_range_article_id(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'page_range_article_id': 'baz-qux',
    }

    obj = StubObj(data, extra_data)

    result = formdata_to_model(obj, formdata)

    assert 'number_of_pages' not in result
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_languages_from_languages(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'language': 'fre'
    }

    obj = StubObj(data, extra_data)

    expected = [
        'French',
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['languages']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_languages_from_other_languages(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'language': 'oth',
        'other_language': 'baz',
    }

    obj = StubObj(data, extra_data)

    expected = [
        'baz',
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['languages']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
def test_formdata_to_model_populates_hidden_notes_from_extra_comments(u, ui):
    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'extra_comments': 'baz',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {
            'source': 'submitter',
            'value': 'baz',
        },
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['hidden_notes']
    assert obj.data == {}


@mock.patch('inspirehep.modules.literaturesuggest.tasks.User')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.UserIdentity')
@mock.patch('inspirehep.modules.literaturesuggest.tasks.JournalsSearch.execute')
def test_formdata_to_model_normalizes_journal_title(e, ui, u):
    e.return_value = Response({
        'hits': {
            'hits': [
                {
                    '_index': 'records-hep',
                    '_type': 'hep',
                    '_id': '42',
                    '_source': {
                        'short_titles': [
                            {'title': 'quux'},
                        ],
                    },
                },
            ],
        },
    })

    data = {}
    extra_data = {}
    formdata = {
        'type_of_doc': 'foo',
        'title': [
            'bar',
        ],
        'journal_title': 'baz',
    }

    obj = StubObj(data, extra_data)

    expected = [
        {'journal_title': 'quux'},
    ]
    result = formdata_to_model(obj, formdata)

    assert expected == result['publication_info']


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
