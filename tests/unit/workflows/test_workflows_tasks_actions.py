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
from mock import patch
import pkg_resources
import pytest
import requests_mock
from flask import current_app
from jsonschema import ValidationError

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.actions import (
    _is_auto_rejected,
    add_core,
    download_documents,
    fix_submission_number,
    halt_record,
    in_production_mode,
    is_arxiv_paper,
    is_experimental_paper,
    is_marked,
    is_record_accepted,
    is_record_relevant,
    is_submission,
    mark,
    populate_journal_coverage,
    populate_submission_document,
    preserve_root,
    reject_record,
    refextract,
    set_refereed_and_fix_document_type,
    shall_halt_workflow,
    validate_record,
)

from mocks import MockEng, MockObj, MockFiles


def _get_auto_reject_obj(decision, has_core_keywords, fulltext_used):
    obj_params = {
        'classifier_results': {
            'complete_output': {
                'core_keywords': ['something'] if has_core_keywords else [],
            },
            'fulltext_used': fulltext_used,
        },
        'relevance_prediction': {
            'max_score': '0.222113',
            'decision': decision,
        },
    }

    return MockObj({}, obj_params)


def test_download_documents():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )

        schema = load_schema('hep')
        subschema = schema['properties']['documents']

        data = {
            'documents': [
                {
                    'key': '1605.03844.pdf',
                    'url': 'http://export.arxiv.org/pdf/1605.03844'
                },
            ],
        }  # literature/1458302
        extra_data = {}
        files = MockFiles({})
        assert validate(data['documents'], subschema) is None

        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert download_documents(obj, eng) is None

        documents = obj.data['documents']
        expected_document_url = '/api/files/0b9dd5d1-feae-4ba5-809d-3a029b0bc110/1605.03844.pdf'

        assert 1 == len(documents)
        assert expected_document_url == documents[0]['url']


def test_download_documents_with_multiple_documents():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03845',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )

        schema = load_schema('hep')
        subschema = schema['properties']['documents']

        data = {
            'documents': [
                {
                    'key': '1605.03844.pdf',
                    'url': 'http://export.arxiv.org/pdf/1605.03844'
                },
                {
                    'key': '1605.03845.pdf',
                    'url': 'http://export.arxiv.org/pdf/1605.03845'
                },
            ],
        }  # literature/1458302
        extra_data = {}
        files = MockFiles({})
        assert validate(data['documents'], subschema) is None

        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert download_documents(obj, eng) is None

        documents = obj.data['documents']
        expected_document_url_1 = '/api/files/0b9dd5d1-feae-4ba5-809d-3a029b0bc110/1605.03844.pdf'
        expected_document_url_2 = '/api/files/0b9dd5d1-feae-4ba5-809d-3a029b0bc110/1605.03845.pdf'

        assert 2 == len(documents)
        assert expected_document_url_1 == documents[0]['url']
        assert expected_document_url_2 == documents[1]['url']


def test_mark():
    obj = MockObj({}, {})
    eng = MockEng()

    foobar_mark = mark('foo', 'bar')

    assert foobar_mark(obj, eng) == {'foo': 'bar'}
    assert obj.extra_data == {'foo': 'bar'}


def test_mark_overwrites():
    obj = MockObj({}, {'foo': 'bar'})
    eng = MockEng()

    foobaz_mark = mark('foo', 'baz')

    assert foobaz_mark(obj, eng) == {'foo': 'baz'}
    assert obj.extra_data == {'foo': 'baz'}


def test_is_marked():
    obj = MockObj({}, {'foo': 'bar'})
    eng = MockEng()

    is_foo_marked = is_marked('foo')

    assert is_foo_marked(obj, eng)


def test_is_marked_returns_false_when_key_does_not_exist():
    obj = MockObj({}, {})
    eng = MockEng()

    is_foo_marked = is_marked('foo')

    assert not is_foo_marked(obj, eng)


def test_is_marked_returns_false_when_value_is_falsy():
    obj = MockObj({}, {'foo': False})
    eng = MockEng()

    is_foo_marked = is_marked('foo')

    assert not is_foo_marked(obj, eng)


def test_is_record_accepted():
    obj = MockObj({}, {'approved': True})

    assert is_record_accepted(obj)


def test_is_record_accepted_returns_false_when_key_does_not_exist():
    obj = MockObj({}, {})

    assert not is_record_accepted(obj)


def test_is_record_accepted_returns_false_when_value_is_falsy():
    obj = MockObj({}, {'approved': False})

    assert not is_record_accepted(obj)


def test_shall_halt_workflow():
    obj = MockObj({}, {'halt_workflow': True})

    assert shall_halt_workflow(obj)


def test_shall_halt_workflow_returns_false_when_key_does_not_exist():
    obj = MockObj({}, {})

    assert not shall_halt_workflow(obj)


def test_shall_halt_workflow_returns_false_when_value_is_falsy():
    obj = MockObj({}, {'halt_workflow': False})

    assert not shall_halt_workflow(obj)


def test_in_production_mode():
    config = {'PRODUCTION_MODE': True}

    with patch.dict(current_app.config, config):
        assert in_production_mode()


def test_in_production_mode_returns_false_when_variable_does_not_exist():
    config = {}

    with patch.dict(current_app.config, config, clear=True):
        assert not in_production_mode()


def test_in_production_mode_returns_false_when_variable_is_falsy():
    config = {'PRODUCTION_MODE': False}

    with patch.dict(current_app.config, config):
        assert not in_production_mode()


def test_add_core_sets_core_to_true_if_extra_data_core_is_true():
    obj = MockObj({}, {'core': True})
    eng = MockEng()

    assert add_core(obj, eng) is None
    assert obj.data == {'core': True}


def test_add_core_sets_core_to_false_if_extra_data_core_is_false():
    obj = MockObj({}, {'core': False})
    eng = MockEng()

    assert add_core(obj, eng) is None
    assert obj.data == {'core': False}


def test_add_core_does_nothing_if_extra_data_has_no_core_key():
    obj = MockObj({}, {})
    eng = MockEng()

    assert add_core(obj, eng) is None
    assert obj.data == {}


def test_add_core_overrides_core_if_extra_data_has_core_key():
    obj = MockObj({'core': False}, {'core': True})
    eng = MockEng()

    assert add_core(obj, eng) is None
    assert obj.data == {'core': True}


def test_halt_record():
    obj = MockObj({}, {'halt_action': 'foo', 'halt_message': 'bar'})
    eng = MockEng()

    default_halt_record = halt_record()

    assert default_halt_record(obj, eng) is None
    assert eng.action == 'foo'
    assert eng.msg == 'bar'


def test_halt_record_accepts_custom_action():
    obj = MockObj({}, {})
    eng = MockEng()

    foo_action_halt_record = halt_record(action='foo')

    assert foo_action_halt_record(obj, eng) is None
    assert eng.action == 'foo'


def test_halt_record_accepts_custom_msg():
    obj = MockObj({}, {})
    eng = MockEng()

    bar_message_halt_record = halt_record(message='bar')

    assert bar_message_halt_record(obj, eng) is None
    assert eng.msg == 'bar'


def test_preserve_root():
    config = {
        'FEATURE_FLAG_ENABLE_MERGER': True
    }

    with patch.dict(current_app.config, config):
        obj = MockObj({'foo': 'bar'}, {})
        eng = MockEng()

        assert preserve_root(obj, eng) is None
        assert obj.extra_data['merger_root'] == {'foo': 'bar'}


@patch('inspirehep.modules.workflows.tasks.actions.log_workflows_action')
def test_reject_record(l_w_a):
    obj = MockObj({}, {
        'relevance_prediction': {
            'max_score': '0.222113',
            'decision': 'Rejected',
        },
    })

    foo_reject_record = reject_record('foo')

    assert foo_reject_record(obj) is None
    assert obj.extra_data == {
        'approved': False,
        'reason': 'foo',
        'relevance_prediction': {
            'decision': 'Rejected',
            'max_score': '0.222113',
        },
    }
    assert obj.log._info.getvalue() == 'foo'
    l_w_a.assert_called_once_with(
        action='reject_record',
        relevance_prediction={
            'decision': 'Rejected',
            'max_score': '0.222113',
        },
        object_id=1,
        user_id=None,
        source='workflow',
    )


@pytest.mark.parametrize(
    'expected,obj',
    [
        (False, _get_auto_reject_obj('Core', has_core_keywords=False, fulltext_used=True)),
        (False, _get_auto_reject_obj('Non-Core', has_core_keywords=False, fulltext_used=True)),
        (True, _get_auto_reject_obj('Rejected', has_core_keywords=False, fulltext_used=True)),
        (False, _get_auto_reject_obj('Core', has_core_keywords=True, fulltext_used=True)),
        (False, _get_auto_reject_obj('Non-Core', has_core_keywords=True, fulltext_used=True)),
        (False, _get_auto_reject_obj('Rejected', has_core_keywords=True, fulltext_used=True)),
        (False, _get_auto_reject_obj('Core', has_core_keywords=False, fulltext_used=False)),
        (False, _get_auto_reject_obj('Non-Core', has_core_keywords=False, fulltext_used=False)),
        (False, _get_auto_reject_obj('Rejected', has_core_keywords=False, fulltext_used=False)),
        (False, _get_auto_reject_obj('Core', has_core_keywords=True, fulltext_used=False)),
        (False, _get_auto_reject_obj('Non-Core', has_core_keywords=True, fulltext_used=False)),
        (False, _get_auto_reject_obj('Rejected', has_core_keywords=True, fulltext_used=False)),
    ],
    ids=[
        'Dont reject: No core keywords (from fulltext) with core decision',
        'Dont reject: No core keywords (from fulltext) with non-core decision',
        'Reject: No core keywords (from fulltext) with rejected decision',
        'Dont reject: Core keywords (from fulltext) with core decision',
        'Dont reject: Core keywords (from fulltext) with non-core decision',
        'Dont reject: Core keywords (from fulltext) with rejected decision',
        'Dont reject: No core keywords (not from fulltext) with core decision',
        'Dont reject: No core keywords (not from fulltext) with non-core decision',
        'Dont reject: No core keywords (not from fulltext) with rejected decision',
        'Dont reject: Core keywords (not from fulltext) with core decision',
        'Dont reject: Core keywords (not from fulltext) with non-core decision',
        'Dont reject: Core keywords (not from fulltext) with rejected decision',
    ]
)
def test__is_auto_rejected(expected, obj):
    assert _is_auto_rejected(obj) is expected


@pytest.mark.parametrize(
    'expected, should_submission, should_auto_reject, should_auto_approve, full_journal_coverage',
    [
        (True, True, True, False, False),
        (True, True, False, False, False),
        (False, False, True, False, False),
        (True, False, False, False, False),
        (True, True, True, True, False),
        (True, True, False, True, False),
        (True, False, True, True, False),
        (True, False, False, True, False),
    ],
    ids=[
        'Relevant: non auto-approved is submission and autorejected',
        'Relevant: non auto-approved is submission and not autorejected',
        'Not relevant: non auto-approved is not submission and autorejected',
        'Relevant: non auto-approved is not submission and not autorejected',
        'Relevant: auto-approved is submission and autorejected',
        'Relevant: auto-approved is submission and not autorejected',
        'Relevant: auto-approved is not submission and autorejected',
        'Relevant: auto-approved is not submission and not autorejected',
    ]
)
@patch('inspirehep.modules.workflows.tasks.actions._is_journal_coverage_full')
@patch('inspirehep.modules.workflows.tasks.actions.is_submission')
@patch('inspirehep.modules.workflows.tasks.actions._is_auto_rejected')
@patch('inspirehep.modules.workflows.tasks.actions._is_auto_approved')
def test_is_record_relevant(
    _is_auto_approved_mock,
    _is_auto_rejected_mock,
    is_submission_mock,
    journal_coverage_full_mock,
    expected,
    should_submission,
    should_auto_reject,
    should_auto_approve,
    full_journal_coverage,
):
    _is_auto_approved_mock.return_value = should_auto_approve
    _is_auto_rejected_mock.return_value = should_auto_reject
    is_submission_mock.return_value = should_submission
    journal_coverage_full_mock.return_value = full_journal_coverage
    obj = object()
    eng = object()

    assert is_record_relevant(obj, eng) is expected


@patch('inspirehep.modules.workflows.tasks.actions.is_submission')
@patch('inspirehep.modules.workflows.tasks.actions._is_auto_rejected')
@patch('inspirehep.modules.workflows.tasks.actions._is_auto_approved')
def test_is_record_relevant_when_journal_coverage_full(
    _is_auto_approved_mock,
    _is_auto_rejected_mock,
    is_submission_mock,
):
    _is_auto_approved_mock.return_value = False
    _is_auto_rejected_mock.return_value = False
    is_submission_mock.return_value = False
    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': 'hep-ex/0008040',
            },
        ],
    }  # literature/532168
    extra_data = {'journal_coverage': 'full'}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_record_relevant(obj, eng)


def test_is_experimental_paper_returns_true_if_obj_has_an_experimental_arxiv_category():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-ex',
                ],
                'value': 'hep-ex/0008040',
            },
        ],
    }  # literature/532168
    extra_data = {}
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_experimental_paper(obj, eng)


def test_is_experimental_paper_returns_true_if_obj_has_an_experimental_inspire_category():
    schema = load_schema('hep')
    subschema = schema['properties']['inspire_categories']

    data = {
        'inspire_categories': [
            {'term': 'Experiment-HEP'},
        ],
    }  # literature/532168
    extra_data = {}
    assert validate(data['inspire_categories'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_experimental_paper(obj, eng)


def test_is_experimental_paper_returns_false_otherwise():
    obj = MockObj({}, {})
    eng = MockEng()

    assert not is_experimental_paper(obj, eng)


def test_is_experimental_paper_does_not_raise_if_obj_has_no_arxiv_category():
    schema = load_schema('hep')
    subschema = schema['properties']['arxiv_eprints']

    data = {
        'arxiv_eprints': [
            {'value': '1712.02280'},
        ],
    }
    extra_data = {}
    assert validate(data['arxiv_eprints'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_experimental_paper(obj, eng)


def test_is_arxiv_paper_returns_false_if_acquision_source_is_not_present():
    obj = MockObj({}, {})
    eng = MockEng()

    assert not is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_returns_false_if_method_is_not_hepcrawl_or_arxiv():
    schema = load_schema('hep')
    acquisition_source_schema = schema['properties']['acquisition_source']
    arxiv_eprints_schema = schema['properties']['arxiv_eprints']

    data = {
        'acquisition_source': {
            'method': 'batchuploader',
            'source': 'arxiv',
        },
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                ],
                'value': '0801.4782',
            },
        ],
    }
    extra_data = {}
    assert validate(data['acquisition_source'], acquisition_source_schema) is None
    assert validate(data['arxiv_eprints'], arxiv_eprints_schema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_for_submission():
    schema = load_schema('hep')
    acquisition_source_schema = schema['properties']['acquisition_source']
    arxiv_eprints_schema = schema['properties']['arxiv_eprints']

    data = {
        'acquisition_source': {
            'method': 'submitter',
        },
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th',
                ],
                'value': '0801.4782',
            },
        ],
    }
    extra_data = {}
    assert validate(data['acquisition_source'], acquisition_source_schema) is None
    assert validate(data['arxiv_eprints'], arxiv_eprints_schema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_returns_false_when_arxiv_eprints_is_not_present_for_submission():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'submitter',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_for_hepcrawl():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'hepcrawl',
            'source': 'arxiv',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_ignores_case_for_hepcrawl():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'hepcrawl',
            'source': 'arXiv',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_returns_false_if_source_is_not_arxiv_for_hepcrawl():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'hepcrawl',
            'source': 'something else',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_arxiv_paper(obj, eng)


def test_is_arxiv_paper_returns_false_if_source_is_not_present_for_hepcrawl():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'hepcrawl',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert not is_arxiv_paper(obj, eng)


def test_is_submission():
    obj = MockObj({'acquisition_source': {'method': 'submitter'}}, {})
    eng = MockEng()

    assert is_submission(obj, eng)


def test_is_submission_returns_false_if_method_is_not_submission():
    obj = MockObj({'acquisition_source': {'method': 'not-submission'}}, {})
    eng = MockEng()

    assert not is_submission(obj, eng)


def test_is_submission_returns_false_if_obj_has_no_acquisition_source():
    obj = MockObj({}, {})
    eng = MockEng()

    assert not is_submission(obj, eng)


def test_is_submission_returns_false_if_obj_has_falsy_acquisition_source():
    obj = MockObj({}, {})
    eng = MockEng()

    assert not is_submission(obj, eng)


def test_fix_submission_number():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'hepcrawl',
            'submission_number': '751e374a017311e896d6fa163ec92c6a',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    fix_submission_number(obj, eng)

    expected = {
        'method': 'hepcrawl',
        'submission_number': '1',
    }
    result = obj.data['acquisition_source']

    assert validate(result, subschema) is None
    assert expected == result


def fix_submission_number_does_nothing_if_method_is_not_hepcrawl():
    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {
        'acquisition_source': {
            'method': 'submitter',
            'submission_number': '869215',
        },
    }
    extra_data = {}
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    fix_submission_number(obj, eng)

    expected = {
        'method': 'submitter',
        'submission_number': '869215',
    }
    result = obj.data['acquisition_source']

    assert validate(result, subschema) is None
    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_populate_journal_coverage_writes_full_if_any_coverage_is_full(mock_replace_refs):
    schema = load_schema('journals')
    subschema = schema['properties']['_harvesting_info']

    journals = [{'_harvesting_info': {'coverage': 'full'}}]
    assert validate(journals[0]['_harvesting_info'], subschema) is None

    mock_replace_refs.return_value = journals

    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'journal_record': {'$ref': 'http://localhost:/api/journals/1213103'}},
        ],
    }
    extra_data = {}
    assert validate(data['publication_info'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert populate_journal_coverage(obj, eng) is None

    expected = 'full'
    result = obj.extra_data['journal_coverage']

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_populate_journal_coverage_writes_partial_if_all_coverages_are_partial(mock_replace_refs):
    schema = load_schema('journals')
    subschema = schema['properties']['_harvesting_info']

    journals = [{'_harvesting_info': {'coverage': 'partial'}}]
    assert validate(journals[0]['_harvesting_info'], subschema) is None

    mock_replace_refs.return_value = journals

    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'journal_record': {'$ref': 'http://localhost:/api/journals/1212337'}},
        ],
    }
    extra_data = {}
    assert validate(data['publication_info'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert populate_journal_coverage(obj, eng) is None

    expected = 'partial'
    result = obj.extra_data['journal_coverage']

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_populate_journal_coverage_does_nothing_if_no_journal_is_found(mock_replace_refs):
    mock_replace_refs.return_value = []

    data = {}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert populate_journal_coverage(obj, eng) is None
    assert 'journal_coverage' not in obj.extra_data


def test_populate_submission_document():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )

        schema = load_schema('hep')
        subschema = schema['properties']['acquisition_source']

        data = {
            'acquisition_source': {
                'datetime': '2017-11-30T16:38:43.352370',
                'email': 'david.caro@cern.ch',
                'internal_uid': 54252,
                'method': 'submitter',
                'orcid': '0000-0002-2174-4493',
                'source': 'submitter',
                'submission_number': '1',
            },
        }
        extra_data = {
            'submission_pdf': 'http://export.arxiv.org/pdf/1605.03844',
        }
        files = MockFiles({})
        assert validate(data['acquisition_source'], subschema) is None

        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert populate_submission_document(obj, eng) is None

        expected = [
            {
                'fulltext': True,
                'key': 'fulltext.pdf',
                'original_url': 'http://export.arxiv.org/pdf/1605.03844',
                'source': 'submitter',
                'url': 'http://export.arxiv.org/pdf/1605.03844',
            },
        ]
        result = obj.data['documents']

        assert expected == result


def test_populate_submission_document_does_not_duplicate_documents():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1605.03844',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1605.03844.pdf')),
        )

        schema = load_schema('hep')
        subschema = schema['properties']['acquisition_source']

        data = {
            'acquisition_source': {
                'datetime': '2017-11-30T16:38:43.352370',
                'email': 'david.caro@cern.ch',
                'internal_uid': 54252,
                'method': 'submitter',
                'orcid': '0000-0002-2174-4493',
                'source': 'submitter',
                'submission_number': '1',
            },
        }
        extra_data = {
            'submission_pdf': 'http://export.arxiv.org/pdf/1605.03844',
        }
        files = MockFiles({})
        assert validate(data['acquisition_source'], subschema) is None

        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert populate_submission_document(obj, eng) is None
        assert populate_submission_document(obj, eng) is None

        expected = [
            {
                'fulltext': True,
                'key': 'fulltext.pdf',
                'original_url': 'http://export.arxiv.org/pdf/1605.03844',
                'source': 'submitter',
                'url': 'http://export.arxiv.org/pdf/1605.03844',
            },
        ]
        result = obj.data['documents']

        assert expected == result


def test_populate_submission_document_without_pdf():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://export.arxiv.org/pdf/1707.02785',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '1707.02785.html')),
        )

        schema = load_schema('hep')
        subschema = schema['properties']['acquisition_source']
        data = {
            'acquisition_source': {
                'datetime': '2017-11-30T16:38:43.352370',
                'email': 'david.caro@cern.ch',
                'internal_uid': 54252,
                'method': 'submitter',
                'orcid': '0000-0002-2174-4493',
                'source': 'submitter',
                'submission_number': '1'
            }
        }
        assert validate(data['acquisition_source'], subschema) is None

        extra_data = {
            'submission_pdf': 'http://export.arxiv.org/pdf/1707.02785',
        }
        files = MockFiles({})
        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert populate_submission_document(obj, eng) is None
        assert not obj.data.get('documents')


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_set_refereed_and_fix_document_type(mock_replace_refs):
    schema = load_schema('journals')
    subschema = schema['properties']['refereed']

    journals = [{'refereed': True}]
    assert validate(journals[0]['refereed'], subschema) is None

    mock_replace_refs.return_value = journals

    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    data = {'document_type': ['article']}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_refereed_and_fix_document_type(obj, eng) is None

    expected = True
    result = obj.data['refereed']

    assert validate(result, subschema) is None
    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_set_refereed_and_fix_document_type_handles_journals_that_publish_mixed_content(mock_replace_refs):
    schema = load_schema('journals')
    proceedings_schema = schema['properties']['proceedings']
    refereed_schema = schema['properties']['refereed']

    journals = [{'proceedings': True, 'refereed': True}]
    assert validate(journals[0]['proceedings'], proceedings_schema) is None
    assert validate(journals[0]['refereed'], refereed_schema) is None

    mock_replace_refs.return_value = journals

    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    data = {'document_type': ['article']}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_refereed_and_fix_document_type(obj, eng) is None

    expected = True
    result = obj.data['refereed']

    assert validate(result, subschema) is None
    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_set_refereed_and_fix_document_type_sets_refereed_to_false_if_all_journals_are_not_refereed(mock_replace_refs):
    schema = load_schema('journals')
    subschema = schema['properties']['refereed']

    journals = [{'refereed': False}]
    assert validate(journals[0]['refereed'], subschema) is None

    mock_replace_refs.return_value = journals

    schema = load_schema('hep')
    subschema = schema['properties']['refereed']

    data = {'document_type': ['article']}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_refereed_and_fix_document_type(obj, eng) is None

    expected = False
    result = obj.data['refereed']

    assert validate(result, subschema) is None
    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_set_refereed_and_fix_document_type_replaces_article_with_conference_paper_if_needed(mock_replace_refs):
    schema = load_schema('journals')
    subschema = schema['properties']['proceedings']

    journals = [{'proceedings': True}]
    assert validate(journals[0]['proceedings'], subschema) is None

    mock_replace_refs.return_value = journals

    schema = load_schema('hep')
    subschema = schema['properties']['document_type']

    data = {'document_type': ['article']}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_refereed_and_fix_document_type(obj, eng) is None

    expected = ['conference paper']
    result = obj.data['document_type']

    assert validate(result, subschema) is None
    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.replace_refs')
def test_set_refereed_and_fix_document_type_does_nothing_if_no_journals_were_found(mock_replace_refs):
    mock_replace_refs.return_value = []

    data = {'document_type': ['article']}
    extra_data = {}

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert set_refereed_and_fix_document_type(obj, eng) is None
    assert 'refereed' not in obj.data


def test_validate_record():
    schema = load_schema('hep')

    data = {
        '_collections': [
            'Literature',
        ],
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {}
    assert validate(data, schema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _validate_record = validate_record('hep')

    assert _validate_record(obj, eng) is None


def test_validate_record_raises_when_record_is_invalid():
    schema = load_schema('hep')

    data = {
        'document_type': [
            'article',
        ],
        'titles': [
            {'title': 'Partial Symmetries of Weak Interactions'},
        ],
    }
    extra_data = {}
    with pytest.raises(ValidationError):
        validate(data, schema)

    obj = MockObj(data, extra_data)
    eng = MockEng()

    _validate_record = validate_record('hep')

    with pytest.raises(ValidationError):
        _validate_record(obj, eng)


@patch('inspirehep.modules.workflows.tasks.actions.create_journal_kb_dict', return_value={})
@patch('inspirehep.modules.workflows.tasks.actions.get_document_in_workflow')
@patch(
    'inspirehep.modules.refextract.matcher.match',
    return_value=iter([])
)
def test_refextract_from_text(mock_match, mock_get_document_in_workflow, mock_create_journal_kb_dict):
    """TODO: Make this an integration test and also test reference matching."""

    mock_get_document_in_workflow.return_value.__enter__.return_value = None
    mock_get_document_in_workflow.return_value.__exit__.return_value = None

    schema = load_schema('hep')
    subschema = schema['properties']['acquisition_source']

    data = {'acquisition_source': {'source': 'submitter'}}
    extra_data = {
        'formdata': {
            'references': 'M.R. Douglas, G.W. Moore, D-branes, quivers, and ALE instantons, arXiv:hep-th/9603167',
        },
    }
    assert validate(data['acquisition_source'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert obj.data['references'][0]['raw_refs'][0]['source'] == 'submitter'


@patch('inspirehep.modules.workflows.tasks.actions.create_journal_kb_dict', return_value={})
@patch(
    'inspirehep.modules.refextract.matcher.match',
    return_value=iter([])
)
def test_refextract_from_raw_refs(mock_create_journal_dict, mock_match):
    """TODO: Make this an integration test and also test reference matching."""
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    data = {
        'references': [
            {
                'raw_refs': [
                    {
                        'schema': 'text',
                        'source': 'arXiv',
                        'value': '[37] M. Vallisneri, \u201cUse and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects,\u201d Phys. Rev. D 77, 042001 (2008) doi:10.1103/PhysRevD.77.042001 [gr-qc/0703086 [GR-QC]].'
                    },
                ],
            },
        ],
    }
    assert validate(data['references'], subschema) is None

    obj = MockObj(data, {})
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert 'reference' in obj.data['references'][0]


@patch('inspirehep.modules.workflows.tasks.actions.create_journal_kb_dict', return_value={})
@patch(
    'inspirehep.modules.refextract.matcher.match',
    return_value=iter([])
)
def test_refextract_valid_refs_from_raw_refs(mock_create_journal_dict, mock_match):
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    data = {
        'references': [
            {
                'raw_refs': [
                    {
                        'schema': 'text',
                        'source': 'arXiv',
                        'value': '[37] M. Vallisneri, \u201cUse and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects,\u201d Phys. Rev. D 77, 042001 (2008) doi:10.1103/PhysRevD.77.042001 [gr-qc/0703086 [GR-QC]].'
                    },
                    {
                        'schema': 'text',
                        'source': 'arXiv',
                        'value': '[37] M. Vallisneri, \u201cUse and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects,\u201d Phys. Rev. D 77, 042001 (2008) doi:10.1103/PhysRevD.77.042001 [gr-qc/0703086 [GR-QC]].'
                    },
                ],
            },
        ],
    }
    obj = MockObj(data, {})
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert len(obj.data['references']) == 1
    assert validate(obj.data['references'], subschema) is None


@patch('inspirehep.modules.workflows.tasks.actions.create_journal_kb_dict', return_value={})
@patch('inspirehep.modules.workflows.tasks.actions.get_document_in_workflow')
@patch(
    'inspirehep.modules.refextract.matcher.match',
    return_value=iter([])
)
def test_refextract_valid_refs_from_text(mock_match, mock_get_document_in_workflow, mock_create_journal_kb_dict):
    """TODO: Make this an integration test and also test reference matching."""

    mock_get_document_in_workflow.return_value.__enter__.return_value = None
    mock_get_document_in_workflow.return_value.__exit__.return_value = None

    schema = load_schema('hep')
    refs_subschema = schema['properties']['references']
    acquisition_source_subschema = schema['properties']['acquisition_source']

    data = {'acquisition_source': {'source': 'submitter'}}
    extra_data = {
        'formdata': {
            'references': 'M.R. Douglas, G.W. Moore, D-branes, quivers, and ALE instantons, arXiv:hep-th/9603167\nM.R. Douglas, G.W. Moore, D-branes, quivers, and ALE instantons, arXiv:hep-th/9603167',
        },
    }
    assert validate(data['acquisition_source'], acquisition_source_subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert refextract(obj, eng) is None
    assert len(obj.data['references']) == 1
    assert validate(obj.data['references'], refs_subschema) is None


def test_url_is_correctly_escaped():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://inspirehep.net/api/files/f6b4bd83-52c7-43b7-b99d-24bffcb407ba/0375-9474%2876%2990288-8.xml',
            content=pkg_resources.resource_string(
                __name__, os.path.join('fixtures', '0375-9474%2876%2990288-8.xml')),
        )
        schema = load_schema('hep')
        subschema = schema['properties']['documents']

        data = {
            'documents': [
                {
                    'key': '0375-9474%2876%2990288-8.xml',
                    'url': 'http://inspirehep.net/api/files/f6b4bd83-52c7-43b7-b99d-24bffcb407ba/0375-9474%2876%2990288-8.xml'
                },
            ],
        }
        extra_data = {}
        files = MockFiles({})
        assert validate(data['documents'], subschema) is None

        obj = MockObj(data, extra_data, files=files)
        eng = MockEng()

        assert download_documents(obj, eng) is None

        documents = obj.data['documents']
        expected_document_url = '/api/files/0b9dd5d1-feae-4ba5-809d-3a029b0bc110/0375-9474%252876%252990288-8.xml'

        assert 1 == len(documents)
        assert expected_document_url == documents[0]['url']
