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

from inspirehep.utils.record_getter import get_db_records, get_es_records


def test_get_es_records_handles_empty_lists(app):
    assert get_es_records('lit', []) == []


def test_get_es_records_accepts_lists_of_integers(app):
    records = get_es_records('lit', [4328])

    assert len(records) == 1


def test_get_es_records_accepts_lists_of_strings(app):
    records = get_es_records('lit', ['4328'])

    assert len(records) == 1


def test_get_es_records_finds_right_results(app):
    literature = [1498175, 1090628]
    authors = [983059]

    results = get_es_records('lit', literature + authors)
    recids = {result['control_number'] for result in results}

    assert len(results) == len(literature)
    assert recids == set(literature)


def test_get_db_records_handles_empty_lists(app):
    assert list(get_db_records([])) == []


def test_get_db_records_accepts_integer_pid_values(app):
    records = list(get_db_records([('lit', 4328)]))

    assert len(records) == 1


def test_get_db_records_accepts_string_pid_values(app):
    records = list(get_db_records([('lit', '4328')]))

    assert len(records) == 1


def test_get_db_records_accept_multiple_pid_types(app):
    records = [('lit', 1498175), ('lit', 1090628), ('aut', 983059)]

    results = list(get_db_records(records))

    assert len(results) == 3
