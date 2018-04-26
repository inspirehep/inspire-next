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

import os
import requests
import subprocess

import backoff
import pytest

from inspirehep.testlib.api import InspireApiClient


@pytest.fixture(autouse=True, scope='function')
def init_environment():
    init_db = './scripts/recreate_records --no-populate'
    subprocess.call(init_db.split())


@pytest.fixture
def inspire_client():
    """Share the same client to reuse the same session"""
    # INSPIRE_API_URL is set by k8s when running the test in Jenkins
    inspire_url = os.environ.get('INSPIRE_API_URL', 'http://test-web-e2e.local:5000')
    return InspireApiClient(base_url=inspire_url)


def wait_for(func, *args, **kwargs):
    max_time = kwargs.pop('max_time', 200)
    interval = kwargs.pop('interval', 2)

    decorator = backoff.on_exception(
        backoff.constant,
        AssertionError,
        interval=interval,
        max_time=max_time,
    )
    decorated = decorator(func)
    return decorated(*args, **kwargs)


def test_harvest_non_core_article_goes_in(inspire_client):
    requests.post(
        url='http://mitm-manager.local/config',
        json={'active_scenario': 'harvest_non_core_article_goes_in'},
    )

    inspire_client.holdingpen.run_harvest(
        spider='arXiv',
        workflow='article',
        url='http://export.arxiv.org/oai2',
        sets='physics',
        from_date='2018-03-25',
    )

    def _all_completed():
        hp_entries = inspire_client.holdingpen.get_list_entries()
        try:
            assert len(hp_entries) == 1
            assert all(entry.status == 'COMPLETED' for entry in hp_entries)
        except AssertionError:
            print('Current holdingpen entries: %s' % hp_entries)
            raise
        return hp_entries[0]

    completed_entry = wait_for(_all_completed)
    entry = inspire_client.holdingpen.get_detail_entry(
        completed_entry.workflow_id
    )

    # check workflows goes as expected
    assert entry.status == 'COMPLETED'
    assert entry.core is None
    assert entry.approved is True

    assert entry.title == 'The OLYMPUS Internal Hydrogen Target'
    assert entry.arxiv_eprint == '1404.0579'
    assert entry.doi == '10.1016/j.nima.2014.04.029'
    assert entry.control_number

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == entry.title
