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
import time

import backoff
import pytest

from inspirehep.testlib.api import InspireApiClient
from inspirehep.testlib.api.mitm_client import MITMClient, with_mitmproxy


@pytest.fixture
def inspire_client():
    """Share the same client to reuse the same session"""
    # INSPIRE_API_URL is set by k8s when running the test in Jenkins
    inspire_url = os.environ.get('INSPIRE_API_URL', 'http://test-web-e2e.local:5000')
    return InspireApiClient(base_url=inspire_url)


@pytest.fixture
def mitm_client():
    mitmproxy_url = os.environ.get('MITMPROXY_HOST', 'http://mitm-manager.local')
    return MITMClient(mitmproxy_url)


@pytest.fixture(autouse=True, scope='function')
def init_environment(inspire_client):
    inspire_client.e2e.init_db()
    inspire_client.e2e.init_es()
    inspire_client.e2e.init_fixtures()
    # refresh login session, giving a bit of time
    time.sleep(1)
    inspire_client.login_local()


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


@with_mitmproxy
def test_harvest_non_core_article_goes_in(inspire_client, mitm_client):
    inspire_client.e2e.schedule_crawl(
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

    # check workflow goes as expected
    assert entry.approved is True
    assert entry.arxiv_eprint == '1404.0579'
    assert entry.control_number
    assert entry.core is None
    assert entry.doi == '10.1016/j.nima.2014.04.029'
    assert entry.status == 'COMPLETED'
    assert entry.title == 'The OLYMPUS Internal Hydrogen Target'

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == entry.title

    # check that the external services were actually called
    mitm_client.assert_interaction_used(
        service_name='LegacyService',
        interaction_name='robotupload',
        times=1,
    )


@with_mitmproxy
def test_harvest_core_article_goes_in(inspire_client, mitm_client):
    inspire_client.e2e.schedule_crawl(
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

    # check workflow goes as expected
    assert entry.approved is True
    assert entry.arxiv_eprint == '1404.0579'
    assert entry.control_number
    assert entry.core
    assert entry.doi == '10.1016/j.nima.2014.04.029'
    assert entry.status == 'COMPLETED'
    assert entry.title == 'The OLYMPUS Internal Hydrogen Target'

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == entry.title

    # check that the external services were actually called
    mitm_client.assert_interaction_used(
        service_name='LegacyService',
        interaction_name='robotupload',
        times=1,
    )
    mitm_client.assert_interaction_used(
        service_name='RTService',
        interaction_name='ticket_new',
        times=1,
    )


@with_mitmproxy
def test_harvest_core_article_manual_accept_goes_in(inspire_client, mitm_client):
    inspire_client.e2e.schedule_crawl(
        spider='arXiv',
        workflow='article',
        url='http://export.arxiv.org/oai2',
        sets='q-bio',
        from_date='2018-03-25',
    )

    def _all_in_status(status):
        hp_entries = inspire_client.holdingpen.get_list_entries()
        try:
            assert len(hp_entries) == 1
            assert all(entry.status == status for entry in hp_entries)
        except AssertionError:
            print(
                'Current holdingpen entries (waiting for them to be in %s status): %s'
                % (status, hp_entries)
            )
            raise
        return hp_entries[0]

    halted_entry = wait_for(lambda: _all_in_status('HALTED'))
    entry = inspire_client.holdingpen.get_detail_entry(halted_entry.workflow_id)

    # check workflow gets halted
    assert entry.approved is None
    assert entry.arxiv_eprint == '1404.0579'
    assert entry.control_number is None
    assert entry.core is None
    assert entry.doi == '10.1016/j.nima.2014.04.029'
    assert entry.status == 'HALTED'
    assert entry.title == 'The OLYMPUS Internal Hydrogen Target'

    inspire_client.holdingpen.accept_core(holdingpen_id=entry.workflow_id)

    # check that completed workflow is ok
    completed_entry = wait_for(lambda: _all_in_status('COMPLETED'))
    entry = inspire_client.holdingpen.get_detail_entry(completed_entry.workflow_id)

    assert entry.arxiv_eprint == '1404.0579'
    assert entry.control_number is 42
    assert entry.doi == '10.1016/j.nima.2014.04.029'
    assert entry.title == 'The OLYMPUS Internal Hydrogen Target'

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == entry.title

    # check that the external services were actually called
    mitm_client.assert_interaction_used(
        service_name='LegacyService',
        interaction_name='robotupload',
        times=1,
    )
    mitm_client.assert_interaction_used(
        service_name='RTService',
        interaction_name='ticket_new',
        times=1,
    )


@with_mitmproxy
def test_harvest_nucl_th_and_jlab_curation(inspire_client, mitm_client):
    inspire_client.e2e.schedule_crawl(
        spider='arXiv_single',
        workflow='article',
        url='http://export.arxiv.org/oai2',
        identifier='oai:arXiv.org:1806.05669',  # nucl-th record
    )

    def _all_in_status(status):
        hp_entries = inspire_client.holdingpen.get_list_entries()
        try:
            assert len(hp_entries) == 1
            assert all(entry.status == status for entry in hp_entries)
        except AssertionError:
            print(
                'Current holdingpen entries (waiting for them to be in %s status): %s'
                % (status, hp_entries)
            )
            raise
        return hp_entries[0]

    halted_entry = wait_for(lambda: _all_in_status('COMPLETED'))
    entry = inspire_client.holdingpen.get_detail_entry(halted_entry.workflow_id)

    assert entry.arxiv_eprint == '1806.05669'
    assert entry.control_number is 42
    assert entry.title == 'Probing the in-Medium QCD Force by Open Heavy-Flavor Observables'

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == entry.title

    # check that the external services were actually called
    mitm_client.assert_interaction_used(
        service_name='LegacyService',
        interaction_name='robotupload',
        times=1,
    )
    mitm_client.assert_interaction_used(
        service_name='RTService',
        interaction_name='ticket_new',
        times=1,
    )
