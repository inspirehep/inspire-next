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


from inspirehep.modules.records.facets import range_author_count_filter, must_match_all_filter


def test_range_author_count_filter():
    range_filter = range_author_count_filter('author_count')
    assert range_filter(None).to_dict() == {
        'range': {
            'author_count': {
                'gte': 1,
                'lte': 10,
            },
        },
    }


def test_must_match_all_filter():
    must_filter = must_match_all_filter('facet_author_name')

    values1 = ['John Doe']
    expected1 = {
        'bool': {
            'must': [
                {
                    'match': {
                        'facet_author_name': 'John Doe'
                    }
                }
            ]
        }
    }

    assert must_filter(values1).to_dict() == expected1

    values2 = ['John Doe', 'John Doe 2']
    expected2 = {
        'bool': {
            'must': [
                {
                    'match': {
                        'facet_author_name': 'John Doe'
                    }
                },
                {
                    'match': {
                        'facet_author_name': 'John Doe 2'
                    }
                }
            ]
        }
    }

    assert must_filter(values2).to_dict() == expected2
