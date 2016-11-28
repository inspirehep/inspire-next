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

from inspirehep.modules.records.tasks import find_and_replace_old_link_with_new_link_in_record


def test_json_walker_standard_input():
    json_record = {
        u'date_and_time_of_latest_transaction': u'20160922232729.0',
        u'_collections': [],
        u'control_number': u'333',
        u'publication_info': [{
            u'journal_title': u'IAU Symp.',
            u'cnum': u'C08-06 -09',
            u'journal_volume': u'354',
            u'parent_record': {
                u'$ref': u'http://localhost:5000/api/literature/222'
            },
            u'artid': u'45',
            u'year': 2008,
            u'page_start': u'45'
        }],
        u'self': {
            u'$ref': u'http://localhost:5000/api/literature/333'
        },
        u'$schema': u'http://localhost:5000/schemas/records/hep.json'
    }

    expected = 'http://localhost:5000/api/record/111'
    old_link = 'http://localhost:5000/api/literature/222'

    find_and_replace_old_link_with_new_link_in_record(json_record, expected, old_link)
    test_field = json_record.get('publication_info')[0].get('parent_record').get('$ref')

    assert test_field == expected


def test_json_walker_input_containing_words_with_ref():
    json_record = {
        u'date_and_time_of_latest_transaction': u'20160922232729.0',
        u'_collections': [],
        u'control_number': u'333',
        u'publication_info': [{
            u'journal_title': u'IAU Ref.',
            u'ref': u'C08-06 -09',
            u'journal_$ref': u'354',
            u'parent_record': {
                u'$ref': u'http://localhost:5000/ref/literature/222'
            },
            u'artid': u'45',
            u'year': 2008,
            u'page_start': u'45'
        }],
        u'self': {
            u'$ref': u'http://localhost:5000/api/$ref/333'
        },
        u'$schema': u'$ref://localhost:5000/schemas/records/hep.json'
    }

    expected = 'http://localhost:5000/api/record/111'
    old_link = 'http://localhost:5000/ref/literature/222'

    find_and_replace_old_link_with_new_link_in_record(json_record, expected, old_link)
    test_field = json_record.get('publication_info')[0].get('parent_record').get('$ref')

    assert test_field == expected
