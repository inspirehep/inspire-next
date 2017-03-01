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

from six import StringIO

from inspirehep.modules.workflows.tasks.submission import (
    add_note_entry,
    prepare_files,
)


class MockLog(object):
    def __init__(self):
        self._debug = StringIO()
        self._info = StringIO()

    def debug(self, message):
        self._debug.write(message)

    def info(self, message):
        self._info.write(message)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class StubFiles(object):
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    def __len__(self):
        return len(self.data)

    @property
    def keys(self):
        return self.data.keys()


class StubObj(object):
    def __init__(self, data, extra_data, files):
        self.data = data
        self.extra_data = extra_data
        self.files = files

        self.log = MockLog()


class DummyEng(object):
    pass


def test_add_note_entry_does_not_add_value_that_is_already_present():
    data = {
        'public_notes': [
            {'value': '*Temporary entry*'},
        ],
    }
    extra_data = {'core': 'something'}
    files = StubFiles({})

    obj = StubObj(data, extra_data, files)
    eng = DummyEng()

    assert add_note_entry(obj, eng) is None
    assert obj.data == {
        'public_notes': [
            {'value': '*Temporary entry*'},
        ],
    }


def test_prepare_files():
    data = {}
    extra_data = {}
    files = StubFiles({
        'foo.pdf': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = StubObj(data, extra_data, files)
    eng = DummyEng()

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
    assert '/data/foo.pdf' in obj.log._debug.getvalue()


def test_prepare_files_annotates_files_from_arxiv():
    data = {
        'arxiv_eprints': [
            {'categories': 'hep-th'},
        ],
    }
    extra_data = {}
    files = StubFiles({
        'foo.pdf': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = StubObj(data, extra_data, files)
    eng = DummyEng()

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
    assert '/data/foo.pdf' in obj.log._debug.getvalue()


def test_prepare_files_skips_empty_files():
    data = {}
    extra_data = {}
    files = StubFiles({
        'foo.pdf': AttrDict({}),
    })

    obj = StubObj(data, extra_data, files)
    eng = DummyEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {}
    assert '' == obj.log._info.getvalue()
    assert '' == obj.log._debug.getvalue()


def test_prepare_files_does_nothing_when_obj_has_no_files():
    data = {}
    extra_data = {}
    files = StubFiles({})

    obj = StubObj(data, extra_data, files)
    eng = DummyEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {}
    assert '' == obj.log._info.getvalue()
    assert '' == obj.log._debug.getvalue()


def test_prepare_files_ignores_keys_not_ending_with_pdf():
    data = {}
    extra_data = {}
    files = StubFiles({
        'foo.bar': AttrDict({
            'obj': AttrDict({
                'file': AttrDict({
                    'uri': '/data/foo.pdf',
                }),
            }),
        }),
    })

    obj = StubObj(data, extra_data, files)
    eng = DummyEng()

    assert prepare_files(obj, eng) is None
    assert obj.data == {}
    assert '' == obj.log._info.getvalue()
    assert '' == obj.log._debug.getvalue()
