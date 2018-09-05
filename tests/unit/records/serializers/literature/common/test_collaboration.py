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

import json

from inspirehep.modules.records.serializers.schemas.json.literature.common import CollaborationWithSuffixSchemaV1, CollaborationSchemaV1


def test_collaboration_with_suffix_returns_empty_if_value_has_no_suffix():
    schema = CollaborationWithSuffixSchemaV1()
    dump = {'value': 'CMS'}
    expected = {}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_collaboration_with_suffix_returns_value_if_value_has_suffix():
    schema = CollaborationWithSuffixSchemaV1()
    dump = {'value': 'CMS Team'}
    expected = {'value': 'CMS Team'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_collaboration_returns_empty_if_value_has_suffix():
    schema = CollaborationSchemaV1()
    dump = {'value': 'CMS Team'}
    expected = {}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_collaboration_returns_value_if_value_has_no_suffix():
    schema = CollaborationSchemaV1()
    dump = {'value': 'CMS'}
    expected = {'value': 'CMS'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)
