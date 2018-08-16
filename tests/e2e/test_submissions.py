# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

from inspirehep.testlib.api.author_form import AuthorFormInputData
from inspirehep.testlib.api.literature_form import LiteratureFormInputData
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


@with_mitmproxy
def test_literature_submission_restarts_cleanly(inspire_client, mitm_client):
    modified_title = 'Title Modified'
    original_title = 'Physics of Donut'

    literature_form = LiteratureFormInputData(
        title=original_title,
        type_of_doc='article',
        language='en',
    )
    literature_form.add_author('Simpson, Homer J.')
    inspire_client.literature_form.submit(literature_form)

    halted_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='HALTED',
            num_entries=1,
        )
    )[0]
    workflow_id = halted_entry.workflow_id
    entry = inspire_client.holdingpen.get_detail_entry(workflow_id)

    # Make some changes to the workflow
    entry.titles[0].title = modified_title
    entry.approved = True
    inspire_client.holdingpen.edit_workflow(entry)

    # Assert changes were made
    updated_entry = inspire_client.holdingpen.get_detail_entry(workflow_id)

    updated_title = updated_entry.titles[0].title
    assert updated_title == modified_title
    assert updated_entry.approved

    # Restart the workflow
    inspire_client.holdingpen.restart_workflow(workflow_id)

    # Assert workflow is halted and restored back to original submission
    def _workflow_halted_with_original_data():
        entry = inspire_client.holdingpen.get_detail_entry(workflow_id)
        assert entry.status == 'HALTED'
        assert entry.titles[0].title == original_title
        assert not entry.approved

    wait_for(_workflow_halted_with_original_data)

    mitm_client.assert_interaction_used('RTService', 'ticket_new', times=1)
    mitm_client.assert_interaction_used('RTService', 'ticket_edit', times=1)
    mitm_client.assert_interaction_used('RTService', 'ticket_comment', times=1)


@with_mitmproxy
def test_author_submission_restarts_cleanly(inspire_client, mitm_client):
    modified_name = 'Modified Name'
    original_name = 'Homer Simpson'

    author_form = AuthorFormInputData(
        given_names='Homer Jay',
        family_name='Simpson',
        display_name=original_name,
        status='retired',
        research_field='econ',
    )

    inspire_client.author_form.submit(author_form)

    halted_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='HALTED',
            num_entries=1,
        )
    )[0]
    workflow_id = halted_entry.workflow_id
    entry = inspire_client.holdingpen.get_detail_entry(workflow_id)

    # Make some changes to the workflow
    entry.display_name = modified_name
    entry.approved = True
    inspire_client.holdingpen.edit_workflow(entry)

    # Assert changes were made
    updated_entry = inspire_client.holdingpen.get_detail_entry(workflow_id)

    updated_name = updated_entry.display_name
    assert updated_name == modified_name
    assert updated_entry.approved

    # Restart the workflow
    inspire_client.holdingpen.restart_workflow(workflow_id)

    # Assert workflow is halted and restored back to original submission
    def _workflow_halted_with_original_data():
        entry = inspire_client.holdingpen.get_detail_entry(workflow_id)
        assert entry.status == 'HALTED'
        assert entry.display_name == original_name
        assert not entry.approved

    wait_for(_workflow_halted_with_original_data)

    mitm_client.assert_interaction_used('RTService', 'ticket_new', times=1)
    mitm_client.assert_interaction_used('RTService', 'ticket_edit', times=1)
    mitm_client.assert_interaction_used('RTService', 'ticket_comment', times=1)
