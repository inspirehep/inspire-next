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

from inspirehep.modules.workflows.tasks.merging import get_head_source
from inspirehep.modules.workflows.utils import insert_wf_record_source


@pytest.fixture
def simple_record():
    return {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        '_collections': ['Literature'],
        'document_type': ['article'],
        'titles': [{'title': 'Superconductivity'}],
        "control_number": 1
    }


def test_get_head_source_no_rec_on_the_db_gives_none(app):
    assert get_head_source('7753a30b-1111-2222-3333-d5020069b3ab') is None


def test_get_head_source_return_arxiv_when_one_arxive_source_present(app, simple_record):
    # XXX: for some reason, this must be internal.
    from inspirehep.modules.migrator.tasks import record_insert_or_replace

    rec = record_insert_or_replace(simple_record)
    uuid = rec.id

    # two sources for the same record
    insert_wf_record_source(json=simple_record, record_uuid=uuid, source='ejl')

    assert get_head_source(uuid) == 'publisher'

    insert_wf_record_source(json=simple_record, record_uuid=uuid, source='arxiv')
    assert get_head_source(uuid) == 'arxiv'
