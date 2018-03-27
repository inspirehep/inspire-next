# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import backoff
import pytest
import subprocess

from inspirehep.testlib.fake_arxiv_service import FakeArxivService
from inspirehep.testlib.errors import raise_if_false, RetryError
from inspirehep.testlib.api_clients import InspireApiClient


@pytest.fixture(autouse=True, scope='function')
def init_environment():
    init_db = './scripts/recreate_records'
    subprocess.call(init_db.split())


@pytest.fixture
def inspire_client():
    """Share the same client to reuse the same session"""
    return InspireApiClient()


@backoff.on_exception(backoff.constant, RetryError, interval=10, max_time=200)
def wait_for_n_entries_in_status(inspire_client, entries_number, status):
    hp_entries = inspire_client.holdingpen.get_list_entries()
    raise_if_false(all(entry.status == status for entry in hp_entries))
    raise_if_false(len(hp_entries) == entries_number)
    return hp_entries


def test_harvest_core_article_goes_in(inspire_client):
    arxiv_service = FakeArxivService()
    arxiv_service.run_harvest()

    hp_entries = wait_for_n_entries_in_status(inspire_client, 1, 'COMPLETED')
    assert len(hp_entries) == 1

    entry = inspire_client.holdingpen.get_detail_entry(hp_entries[0].workflow_id)

    # check workflows goes as expected
    assert entry.status == 'COMPLETED'
    assert entry.core is True
    assert entry.approved is True

    assert entry.title == 'Renormalized Quantum Yang-Mills Fields in Curved Spacetime'
    assert entry.arxiv_eprint == '0705.3340'
    assert entry.doi == '10.1142/S0129055X08003420'
    assert entry.control_number

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == entry.title
