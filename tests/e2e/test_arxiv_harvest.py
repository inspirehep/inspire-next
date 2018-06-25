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
import os
import re
import time
import urllib2
import yaml

from inspirehep.testlib.api.holdingpen import HoldingpenResource
from inspirehep.testlib.api.mitm_client import with_mitmproxy


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


def _all_in_status(holdingpen_client, status):
    hp_entries = holdingpen_client.get_list_entries()
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


def _workflows_in_status(holdingpen_client, num_entries, status):
    hp_entries = holdingpen_client.get_list_entries()
    entries_in_status = [entry for entry in hp_entries if entry.status == status]
    try:
        assert len(entries_in_status) == num_entries
    except AssertionError:
        print(
            'Current holdingpen entries (waiting for %s of them to be in %s status): %s'
            % (num_entries, status, hp_entries)
        )
        raise
    return entries_in_status


def _number_of_entries(holdingpen_client, num_entries):
    hp_entries = holdingpen_client.get_list_entries()
    try:
        assert len(hp_entries) == num_entries, (
            'Current holdingpen entries (waiting for them to be in %d current number): %d'
            % (num_entries, len(hp_entries))
        )
    except AssertionError:
        raise
    return hp_entries


@with_mitmproxy
def test_harvest_non_core_article_goes_in(inspire_client, mitm_client):
    inspire_client.e2e.schedule_crawl(
        spider='arXiv',
        workflow='article',
        url='http://export.arxiv.org/oai2',
        sets='physics',
        from_date='2018-03-25',
    )

    completed_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='COMPLETED',
            num_entries=1,
        )
    )[0]
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

    completed_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='COMPLETED',
            num_entries=1,
        )
    )[0]
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
    assert not entry.is_update

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

    # update
    inspire_client.e2e.schedule_crawl(
        spider='arXiv',
        workflow='article',
        url='http://export.arxiv.org/oai2',
        sets='physics',
        from_date='2018-03-26',
    )

    update_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            num_entries=1,
            status='HALTED'
        )
    )[0]
    update_entry = inspire_client.holdingpen.get_detail_entry(
        update_entry.workflow_id
    )

    # check workflow goes as expected
    assert update_entry.auto_approved is True
    assert update_entry.arxiv_eprint == '1404.0579'
    assert update_entry.core
    assert update_entry.doi == '10.1016/j.nima.2014.04.029'
    assert update_entry.status == 'HALTED'
    # due to the conflict and merge, the title is the old one
    assert update_entry.title == 'The OLYMPUS Internal Hydrogen Target updated'
    assert update_entry.is_update
    assert update_entry.approved_match == entry.control_number

    inspire_client.holdingpen.resolve_merge_conflicts(hp_entry=update_entry)

    wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='COMPLETED',
            num_entries=2,
        )
    )
    update_entry = inspire_client.holdingpen.get_detail_entry(
        update_entry.workflow_id
    )

    # check workflow goes as expected
    assert update_entry.auto_approved is True
    assert update_entry.arxiv_eprint == '1404.0579'
    assert update_entry.core
    assert update_entry.doi == '10.1016/j.nima.2014.04.029'
    assert update_entry.status == 'COMPLETED'
    # due to the conflict and merge, the title is the old one
    assert update_entry.title == 'The OLYMPUS Internal Hydrogen Target updated'
    assert update_entry.is_update
    assert update_entry.approved_match == entry.control_number

    # check literature record is available and consistent
    record = inspire_client.literature.get_record(update_entry.control_number)
    assert record.title == update_entry.title

    # check that the external services were actually called, the updates flag
    # is disabled
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

    halted_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='HALTED',
            num_entries=1,
        )
    )[0]
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
    completed_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='COMPLETED',
            num_entries=1,
        )
    )[0]
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

    completed_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='COMPLETED',
            num_entries=1,
        )
    )[0]
    entry = inspire_client.holdingpen.get_detail_entry(completed_entry.workflow_id)

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

    def _get_ticket_content():
        curr_path = os.path.dirname(__file__)
        ticket_file = os.path.join(curr_path, 'scenarios', 'harvest_nucl_th_and_jlab_curation', 'RTService', 'ticket_new.yaml')
        content = yaml.load(open(ticket_file))
        ticket_content = urllib2.unquote(content['request']['body']).decode('utf8')
        return re.search('\/workflows\/edit_article\/[0-9]+', ticket_content).group(0)

    curation_link = _get_ticket_content()
    assert inspire_client._client.get(curation_link).status_code == 200

    new_entries = wait_for(lambda: _number_of_entries(inspire_client.holdingpen, 2))
    assert len(new_entries) == 2
    edit_article_wf = filter(lambda entry: entry.status == 'WAITING', new_entries)[0]

    entry = inspire_client.holdingpen.get_detail_entry(edit_article_wf.workflow_id)

    def apply_changes_to_wf():
        new_title = 'Title changed by JLab curator'
        curated_content = entry._raw_json
        curated_content['metadata']['titles'][0]['title'] = new_title
        return HoldingpenResource.from_json(curated_content)

    entry = apply_changes_to_wf()
    inspire_client.holdingpen.resume(entry)

    entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='COMPLETED',
            num_entries=1,
        )
    )[0]
    entry = inspire_client.holdingpen.get_detail_entry(entry.workflow_id)

    time.sleep(5)
    # check literature record is available and consistent
    record = inspire_client.literature.get_record(entry.control_number)
    assert record.title == 'Title changed by JLab curator'
