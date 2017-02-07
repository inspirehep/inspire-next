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

import pytest
from mock import patch
from six import StringIO

from inspirehep.modules.workflows.tasks.actions import (
    mark,
    is_marked,
    is_record_accepted,
    shall_halt_workflow,
    in_production_mode,
    add_core,
    halt_record,
    update_note,
    reject_record,
    is_record_relevant,
    is_experimental_paper,
    is_arxiv_paper,
    is_submission,
    prepare_update_payload,
)


class MockLog(object):
    def __init__(self):
        self._log = StringIO()

    def info(self, message):
        self._log.write(message)


class StubObj(object):
    def __init__(self, data, extra_data):
        self.data = data
        self.extra_data = extra_data


class MockObj(object):

    log = MockLog()

    def __init__(self, id_, data, extra_data):
        self.id = id_
        self.data = data
        self.extra_data = extra_data


class DummyEng(object):
    pass


class MockEng(object):
    def halt(self, action, msg):
        self.action = action
        self.msg = msg


def test_mark():
    obj = StubObj({}, {})
    eng = DummyEng()

    foobar_mark = mark('foo', 'bar')

    assert foobar_mark(obj, eng) is None
    assert obj.extra_data == {'foo': 'bar'}


def test_mark_overwrites():
    obj = StubObj({}, {'foo': 'bar'})
    eng = DummyEng()

    foobaz_mark = mark('foo', 'baz')

    assert foobaz_mark(obj, eng) is None
    assert obj.extra_data == {'foo': 'baz'}


def test_is_marked():
    obj = StubObj({}, {'foo': 'bar'})
    eng = DummyEng()

    is_foo_marked = is_marked('foo')

    assert is_foo_marked(obj, eng)


def test_is_marked_returns_false_when_key_does_not_exist():
    obj = StubObj({}, {})
    eng = DummyEng()

    is_foo_marked = is_marked('foo')

    assert not is_foo_marked(obj, eng)


def test_is_marked_returns_false_when_value_is_falsy():
    obj = StubObj({}, {'foo': False})
    eng = DummyEng()

    is_foo_marked = is_marked('foo')

    assert not is_foo_marked(obj, eng)


def test_is_record_accepted():
    obj = StubObj({}, {'approved': True})

    assert is_record_accepted(obj)


def test_is_record_accepted_returns_false_when_key_does_not_exist():
    obj = StubObj({}, {})

    assert not is_record_accepted(obj)


def test_is_record_accepted_returns_false_when_value_is_falsy():
    obj = StubObj({}, {'approved': False})

    assert not is_record_accepted(obj)


def test_shall_halt_workflow():
    obj = StubObj({}, {'halt_workflow': True})

    assert shall_halt_workflow(obj)


def test_shall_halt_workflow_returns_false_when_key_does_not_exist():
    obj = StubObj({}, {})

    assert not shall_halt_workflow(obj)


def test_shall_halt_workflow_returns_false_when_value_is_falsy():
    obj = StubObj({}, {'halt_workflow': False})

    assert not shall_halt_workflow(obj)


@patch('inspirehep.modules.workflows.tasks.actions.current_app.config', {'PRODUCTION_MODE': True})
def test_in_production_mode():
    assert in_production_mode()


@patch('inspirehep.modules.workflows.tasks.actions.current_app.config', {})
def test_in_production_mode_returns_false_when_variable_does_not_exist():
    assert not in_production_mode()


@patch('inspirehep.modules.workflows.tasks.actions.current_app.config', {'PRODUCTION_MODE': False})
def test_in_production_mode_returns_false_when_variable_is_falsy():
    assert not in_production_mode()


def test_add_core():
    obj = StubObj({}, {'core': True})
    eng = DummyEng()

    assert add_core(obj, eng) is None
    assert obj.data['collections'] == [{'primary': 'CORE'}]


def test_add_core_appends_core_collection_to_existing_collections():
    obj = StubObj({'collections': [{'primary': 'HEP'}]}, {'core': True})
    eng = DummyEng()

    assert add_core(obj, eng) is None
    assert obj.data['collections'] == [
        {'primary': 'HEP'},
        {'primary': 'CORE'},
    ]


def test_add_core_does_nothing_if_obj_was_not_marked_as_core():
    obj = StubObj({}, {})
    eng = DummyEng()

    assert add_core(obj, eng) is None
    assert obj.data == {}


def test_add_core_does_nothing_if_obj_core_mark_is_falsy():
    obj = StubObj({}, {'core': False})
    eng = DummyEng()

    assert add_core(obj, eng) is None
    assert obj.data == {}


def test_add_core_does_nothing_if_obj_is_already_in_core_collection():
    obj = StubObj({'collections': [{'primary': 'CORE'}]}, {'core': True})
    eng = DummyEng()

    assert add_core(obj, eng) is None
    assert obj.data['collections'] == [{'primary': 'CORE'}]


def test_halt_record():
    obj = StubObj({}, {'halt_action': 'foo', 'halt_message': 'bar'})
    eng = MockEng()

    default_halt_record = halt_record()

    assert default_halt_record(obj, eng) is None
    assert eng.action == 'foo'
    assert eng.msg == 'bar'


def test_halt_record_accepts_custom_action():
    obj = StubObj({}, {})
    eng = MockEng()

    foo_action_halt_record = halt_record(action='foo')

    assert foo_action_halt_record(obj, eng) is None
    assert eng.action == 'foo'


def test_halt_record_accepts_custom_msg():
    obj = StubObj({}, {})
    eng = MockEng()

    bar_message_halt_record = halt_record(message='bar')

    assert bar_message_halt_record(obj, eng) is None
    assert eng.msg == 'bar'


def test_update_note():
    metadata = {
        'public_notes': [
            {'value': '*Brief entry*'},
        ],
    }

    expected = {
        'public_notes': [
            {'value': '*Temporary entry*'},
        ]
    }
    result = update_note(metadata)

    assert expected == result


def test_update_note_preserves_other_notes():
    metadata = {
        'public_notes': [
            {'value': '*Brief entry*'},
            {'value': 'Other note'},
        ],
    }

    expected = {
        'public_notes': [
            {'value': '*Temporary entry*'},
            {'value': 'Other note'},
        ]
    }
    result = update_note(metadata)

    assert expected == result


@patch('inspirehep.modules.workflows.tasks.actions.log_workflows_action')
def test_reject_record(l_w_a):
    obj = MockObj(1, {}, {
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
    assert obj.log._log.getvalue() == 'foo'
    l_w_a.assert_called_once_with(
        action='reject_record',
        prediction_results={
            'decision': 'Rejected',
            'max_score': '0.222113',
        },
        object_id=1,
        user_id=0,
        source='workflow',
    )


def test_is_record_relevant():
    obj = StubObj({}, {
        'classifier_results': {
            'complete_output': {
                'Core keywords': [],
            },
        },
        'prediction_results': {
            'max_score': '0.222113',
            'decision': 'Rejected',
        },
    })
    eng = DummyEng()

    assert not is_record_relevant(obj, eng)


def test_is_record_relevant_returns_true_if_it_is_a_submission():
    obj = StubObj({'acquisition_source': {'method': 'submitter'}}, {})
    eng = DummyEng()

    assert is_record_relevant(obj, eng)


def test_is_record_relevant_returns_true_if_no_prediction_results():
    obj = StubObj({}, {
        'classifier_results': {
            'complete_output': {
                'Core keywords': [],
            },
        },
    })
    eng = DummyEng()

    assert is_record_relevant(obj, eng)


def test_is_record_relevant_returns_true_if_no_classifier_results():
    obj = StubObj({}, {
        'prediction_results': {
            'max_score': '0.222113',
            'decision': 'Rejected',
        },
    })
    eng = DummyEng()

    assert is_record_relevant(obj, eng)


def test_is_experimental_paper():
    obj = StubObj({
        'arxiv_eprints': [
            {'categories': ['hep-ex']},
        ]
    }, {})
    eng = DummyEng()

    assert is_experimental_paper(obj, eng)


def test_is_experimental_paper_returns_true_if_inspire_categories_in_list():
    obj = StubObj({'inspire_categories': [{'term': 'Experiment-HEP'}]}, {})
    eng = DummyEng()

    assert is_experimental_paper(obj, eng)


def test_is_experimental_paper_returns_false_otherwise():
    obj = StubObj({}, {})
    eng = DummyEng()

    assert not is_experimental_paper(obj, eng)


def test_is_arxiv_paper():
    obj = StubObj({
        'arxiv_eprints': [
            {
                'categories': ['hep-th'],
                'value': 'oai:arXiv.org:0801.4782',
            },
        ],
    }, {})

    assert is_arxiv_paper(obj)


def test_is_arxiv_paper_returns_false_when_arxiv_eprints_is_empty():
    obj = StubObj({'arxiv_eprints': []}, {})

    assert not is_arxiv_paper(obj)


def test_is_submission():
    obj = StubObj({'acquisition_source': {'method': 'submitter'}}, {})
    eng = DummyEng()

    assert is_submission(obj, eng)


def test_is_submission_returns_false_if_method_is_not_submission():
    obj = StubObj({'acquisition_source': {'method': 'not-submission'}}, {})
    eng = DummyEng()

    assert not is_submission(obj, eng)


def test_is_submission_returns_false_if_obj_has_no_acquisition_source():
    obj = StubObj({}, {})
    eng = DummyEng()

    assert not is_submission(obj, eng)


def test_is_submission_returns_false_if_obj_has_falsy_acquisition_source():
    obj = StubObj({}, {})
    eng = DummyEng()

    assert not is_submission(obj, eng)


def test_prepare_update_payload():
    obj = StubObj({}, {})
    eng = DummyEng()

    default_prepare_update_payload = prepare_update_payload()

    assert default_prepare_update_payload(obj, eng) is None
    assert obj.extra_data['update_payload'] == {}


def test_prepare_update_payload_accepts_a_custom_key():
    obj = StubObj({}, {})
    eng = DummyEng()

    custom_key_prepare_update_payload = prepare_update_payload('custom_key')

    assert custom_key_prepare_update_payload(obj, eng) is None
    assert obj.extra_data['custom_key'] == {}


def test_prepare_update_payload_overwrites():
    obj = StubObj({'bar': 'baz'}, {'foo': 'foo'})
    eng = DummyEng()

    foo_prepare_update_payload = prepare_update_payload('foo')

    assert foo_prepare_update_payload(obj, eng) is None
    assert obj.extra_data['foo'] == {'bar': 'baz'}
