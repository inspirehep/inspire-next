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
def test_literature_submission_has_source_data(inspire_client, mitm_client):
    literature_form = LiteratureFormInputData(
        title='Physics of Donut',
        type_of_doc='article',
        language='en',
    )
    literature_form.add_author('Simpson, Homer J.')
    inspire_client.literature_form.submit(literature_form)

    completed_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='HALTED',
            num_entries=1,
        )
    )[0]
    entry = inspire_client.holdingpen.get_detail_entry(
        completed_entry.workflow_id
    )

    result_source_data = entry.extra_data['source_data']

    assert result_source_data['data']
    assert result_source_data['extra_data']


@with_mitmproxy
def test_author_submission_has_source_data(inspire_client, mitm_client):
    author_form = AuthorFormInputData(
        given_names='Homer Jay',
        family_name='Simpson',
        display_name='Homer Simpson',
        status='retired',
        research_field='econ',
    )

    inspire_client.author_form.submit(author_form)

    completed_entry = wait_for(
        lambda: _workflows_in_status(
            holdingpen_client=inspire_client.holdingpen,
            status='HALTED',
            num_entries=1,
        )
    )[0]
    entry = inspire_client.holdingpen.get_detail_entry(
        completed_entry.workflow_id
    )

    assert entry.display_name == 'Homer Simpson'

    result_source_data = entry.extra_data['source_data']

    assert result_source_data['data']
    assert result_source_data['extra_data']
