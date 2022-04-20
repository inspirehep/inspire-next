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

from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.refextract.tasks import create_journal_kb_file
from inspirehep.utils.record_getter import get_db_record


@pytest.fixture
def jhep_with_malformed_title(app):
    """Temporarily add a malformed title to the JHEP record."""
    record = get_db_record('jou', 1213103)
    record['title_variants'].append('+++++')
    record = InspireRecord.create_or_update(record)
    record.commit()

    yield

    record = get_db_record('jou', 1213103)
    record['title_variants'] = record['title_variants'][:-1]
    record = InspireRecord.create_or_update(record)
    record.commit()


@pytest.fixture
def jhep_deleted(app):
    """Temporarily delete record."""
    record = get_db_record('jou', 1213103)
    record['deleted'] = True
    record = InspireRecord.create_or_update(record)
    record.commit()

    yield

    record = get_db_record('jou', 1213103)
    del record['deleted']
    record = InspireRecord.create_or_update(record)
    record.commit()


def test_create_journal_kb_file(app, tmpdir):
    journal_kb_fd = tmpdir.join('journal-titles.kb')

    config = {'REFEXTRACT_JOURNAL_KB_PATH': str(journal_kb_fd)}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    journal_kb = journal_kb_fd.read().splitlines()

    # short_title -> short_title
    assert 'JHEP---JHEP' in journal_kb

    # journal_title.title -> short_title, normalization is applied
    assert 'THE JOURNAL OF HIGH ENERGY PHYSICS JHEP---JHEP' in journal_kb

    # title_variants -> short_title
    assert 'JOURNAL OF HIGH ENERGY PHYSICS---JHEP' in journal_kb


def test_create_journal_kb_file_handles_malformed_title_variants(jhep_with_malformed_title, tmpdir):
    journal_kb_fd = tmpdir.join('journal-titles.kb')

    config = {'REFEXTRACT_JOURNAL_KB_PATH': str(journal_kb_fd)}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    journal_kb = journal_kb_fd.read().splitlines()

    assert '---JHEP' not in journal_kb


def test_create_journal_kb_file_handles_deleted_journals(jhep_deleted, tmpdir):
    journal_kb_fd = tmpdir.join('journal-titles.kb')

    config = {'REFEXTRACT_JOURNAL_KB_PATH': str(journal_kb_fd)}

    with patch.dict(current_app.config, config):
        create_journal_kb_file()

    journal_kb = journal_kb_fd.read().splitlines()

    assert '---JHEP' not in journal_kb
