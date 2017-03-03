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

from inspirehep.modules.pidstore.utils import (
    get_endpoint_from_pid_type,
    get_pid_type_from_endpoint,
    get_pid_type_from_schema,
)


def test_get_endpoint_from_pid_type():
    expected = 'literature'
    result = get_endpoint_from_pid_type('lit')

    assert expected == result


def test_get_pid_type_from_endpoint():
    expected = 'lit'
    result = get_pid_type_from_endpoint('literature')

    assert expected == result


def test_get_pid_type_from_schema():
    expected = 'lit'
    result = get_pid_type_from_schema('http://localhost:5000/schemas/record/hep.json')

    assert expected == result


def test_get_pid_from_schema_supports_relative_urls():
    expected = 'aut'
    result = get_pid_type_from_schema('schemas/record/authors.json')

    assert expected == result
