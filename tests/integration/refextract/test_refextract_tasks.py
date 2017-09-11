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
from tempfile import mkstemp

import pytest
from flask import current_app
from mock import patch

from inspirehep.modules.migrator.tasks import record_insert_or_replace
from inspirehep.modules.refextract.tasks import create_journal_kb_file
from inspirehep.utils.record_getter import get_db_record


@pytest.fixture
def jhep_with_malformed_title(app):
    """Temporarily add a malformed title to the JHEP record."""
    record = get_db_record('jou', 1213103)
    record['title_variants'].append('+++++')
    record_insert_or_replace(record)

    yield

    record = get_db_record('jou', 1213103)
    record['title_variants'] = record['title_variants'][:-1]
    record_insert_or_replace(record)


def test_create_journal_kb_file(app):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    with open(path, 'r') as fd:
        journal_kb = fd.read().splitlines()

        assert 'JHEP---JHEP' in journal_kb
        '''short_title -> short_title'''

        assert 'THE JOURNAL OF HIGH ENERGY PHYSICS JHEP---JHEP' in journal_kb
        '''journal_title.title -> short_title, normalization is applied'''

        assert 'JOURNAL OF HIGH ENERGY PHYSICS---JHEP' in journal_kb
        '''title_variants -> short_title'''

    os.close(temporary_fd)
    os.remove(path)


def test_create_journal_kb_file_handles_malformed_title_variants(jhep_with_malformed_title):
    temporary_fd, path = mkstemp()
    config = {'REFEXTRACT_JOURNAL_KB_PATH': path}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    with open(path, 'r') as fd:
        journal_kb = fd.read().splitlines()

        assert '---JHEP' not in journal_kb

    os.close(temporary_fd)
    os.remove(path)
