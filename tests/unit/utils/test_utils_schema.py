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

from inspirehep.utils.schema import ensure_valid_schema


def test_ensure_valid_schema_invalid():
    record = {
        '$schema': 'authors.json'
    }

    expected = {
        '$schema': 'http://localhost:5000/schemas/records/authors.json'
    }
    ensure_valid_schema(record)

    assert record == expected


def test_ensure_valid_schema_already_valid():
    record = {
        '$schema': 'https://labs.inspirehep.net/schemas/records/authors.json'
    }

    expected = {
        '$schema': 'https://labs.inspirehep.net/schemas/records/authors.json'
    }
    ensure_valid_schema(record)

    assert record == expected
