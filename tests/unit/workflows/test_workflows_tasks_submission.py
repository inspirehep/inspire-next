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

from mock import MagicMock
import mock

from inspirehep.modules.workflows.tasks.submission import (
    add_note_entry,
    prepare_files,
)


class StubObj(object):
    def __init__(self, data, extra_data):
        self.data = data
        self.extra_data = extra_data


class DummyEng(object):
    pass


class MockFilesCollectionIterator(object):
    def __init__(self, data):
        self.data = data

    @property
    def keys(self):
        return self.data.keys()

    def __getitem__(self, item):
        return self.data[item]


def test_add_note_entry_does_not_add_value_that_is_already_present():
    obj = StubObj({'public_notes': [{'value': '*Temporary entry*'}]}, {'core': 'something'})
    eng = DummyEng()

    assert add_note_entry(obj, eng) is None
    assert {'public_notes': [{'value': '*Temporary entry*'}]} == obj.data


@mock.patch('inspirehep.modules.workflows.tasks.submission.is_arxiv_paper')
def test_prepare_file(fake_is_arxiv_paper):
    eng = DummyEng()
    mock_file = MagicMock()
    files_collection = MagicMock()
    fake_is_arxiv_paper.return_value = True

    mock_file.name = MagicMock(return_value='fake_record')
    mock_file.obj.file.uri = 'fake_uri'

    files_collection.data = {}
    files_collection.files = MockFilesCollectionIterator({
        'fake_record.pdf': mock_file
    })

    assert prepare_files(files_collection, eng) is None
    assert [{'url': '/code/fake_uri',
            'filetype': '.pdf',
            'docfile_type': 'INSPIRE-PUBLIC',
            'filename': 'arxiv:fake_record'}] == files_collection.data['fft']


@mock.patch('inspirehep.modules.workflows.tasks.submission.is_arxiv_paper')
def test_prepare_file_wrong(fake_is_arxiv_paper):
    eng = DummyEng()
    mock_file = MagicMock()
    files_collection = MagicMock()
    fake_is_arxiv_paper.return_value = True

    mock_file.name = MagicMock(return_value='fake_record')
    mock_file.obj.file.uri = 'fake_uri'

    files_collection.data = {}
    files_collection.files = MockFilesCollectionIterator({
        'fake_record.txt': mock_file,
        'fake_record': mock_file,
        '': mock_file,
        'fake_record1.pdf': None,
    })

    assert prepare_files(files_collection, eng) is None
    assert files_collection.data['fft'] == []
