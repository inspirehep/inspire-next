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

from flask import current_app
from mock import patch

from inspirehep.modules.workflows.tasks.submission import (
    add_note_entry,
    create_ticket,
    prepare_files,
)

from mocks import AttrDict, MockEng, MockFiles, MockObj, MockUser


class StubRTInstance(object):
    def create_ticket(self, **kwargs):
        return 1


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
def test_create_ticket_handles_unicode_when_not_in_production_mode(r_t, user):
    user.query.get.return_value = MockUser('user@example.com')
    r_t.return_value = u'φοο'

    config = {'PRODUCTION_MODE': False}

    with patch.dict(current_app.config, config):
        data = {}
        extra_data = {}
        files = MockFiles({})

        obj = MockObj(data, extra_data, files)
        eng = MockEng()

        _create_ticket = create_ticket(None)

        expected = (
            u'Was going to create ticket: None\n\nφοο\n\n'
            u'To: user@example.com Queue: Test'
        )

        assert _create_ticket(obj, eng) is None
        assert expected == obj.log._info.getvalue()


@patch('inspirehep.modules.workflows.tasks.submission.User')
@patch('inspirehep.modules.workflows.tasks.submission.render_template')
@patch('inspirehep.modules.workflows.tasks.submission.get_instance')
def test_create_ticket_handles_unicode_when_in_production_mode(g_i, r_t, user):
    user.query.get.return_value = MockUser('user@example.com')
    r_t.return_value = u'φοο'
    g_i.return_value = StubRTInstance()

    config = {'PRODUCTION_MODE': True}

    with patch.dict(current_app.config, config):
        data = {}
        extra_data = {}
        files = MockFiles({})

        obj = MockObj(data, extra_data, files)
        eng = MockEng()

        _create_ticket = create_ticket(None)

        assert _create_ticket(obj, eng) is None
        assert obj.extra_data == {'ticket_id': 1}
        assert u'Ticket 1 created:\nφοο' in obj.log._info.getvalue()


def test_add_note_entry_does_not_add_value_that_is_already_present():
    data = {
        'public_notes': [
            {'value': '*Temporary entry*'},
        ],
    }
    extra_data = {'core': 'something'}
    files = MockFiles({})

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    assert add_note_entry(obj, eng) is None
    assert obj.data == {
        'public_notes': [
            {'value': '*Temporary entry*'},
        ],
    }


def test_prepare_files():
    data = {}
    extra_data = {}
    files = MockFiles({
        'foo.pdf': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {
        '_fft': [
            {
                'path': '/data/foo.pdf',
                'type': 'INSPIRE-PUBLIC',
                'filename': 'foo',
                'format': '.pdf',
            },
        ],
    }
    assert 'Non-user PDF files added to FFT.' == obj.log._info.getvalue()


def test_prepare_files_annotates_files_from_arxiv():
    data = {
        'arxiv_eprints': [
            {'categories': 'hep-th'},
        ],
    }
    extra_data = {}
    files = MockFiles({
        'foo.pdf': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {
        'arxiv_eprints': [
            {'categories': 'hep-th'},
        ],
        '_fft': [
            {
                'path': '/data/foo.pdf',
                'type': 'arXiv',
                'filename': 'arxiv:foo',
                'format': '.pdf',
            },
        ],
    }
    assert 'Non-user PDF files added to FFT.' == obj.log._info.getvalue()


def test_prepare_files_skips_empty_files():
    data = {}
    extra_data = {}
    files = MockFiles({
        'foo.pdf': AttrDict({}),
    })

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {}
    assert '' == obj.log._info.getvalue()


def test_prepare_files_does_nothing_when_obj_has_no_files():
    data = {}
    extra_data = {}
    files = MockFiles({})

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {}
    assert '' == obj.log._info.getvalue()


def test_prepare_files_ignores_keys_not_ending_with_pdf():
    data = {}
    extra_data = {}
    files = MockFiles({
        'foo.bar': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = MockObj(data, extra_data, files)
    eng = MockEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {}
    assert '' == obj.log._info.getvalue()
