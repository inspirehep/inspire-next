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

import mock

from inspirehep.utils.search import _collection_to_index, get_number_of_records


@mock.patch(
    'inspirehep.utils.search.current_app.config',
    {'SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING': {'foo': 'bar'}})
def test_collection_to_index_fetches_from_mapping():
    expected = 'bar'
    result = _collection_to_index('foo')

    assert expected == result


@mock.patch(
    'inspirehep.utils.search.current_app.config',
    {'SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING': {'foo': 'bar'}})
def test_collection_to_index_falls_back_to_records_hep_if_no_key():
    expected = 'records-hep'
    result = _collection_to_index('baz')

    assert expected == result


@mock.patch('inspirehep.utils.search.current_app.config', {})
def test_collection_to_index_falls_back_to_records_hep_if_no_mapping():
    expected = 'records-hep'
    result = _collection_to_index('foo')

    assert expected == result


@mock.patch('inspirehep.utils.search.current_search_client.count')
def test_get_number_of_records(count):
    count.return_value = {
        "count" : 10,
        "_shards" : {
            "total" : 5,
            "successful" : 5,
            "failed" : 0
        }
    }

    expected = 10
    result = get_number_of_records('foo')

    assert expected == result
