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

from inspirehep.modules.records.serializers.schemas.json.literature.common import PublicationInfoItemSchemaV1


def test_returns_empty_if_display_fields_missing():
    schema = PublicationInfoItemSchemaV1()
    dump = {'journal_issue': 'Test'}
    expected = {}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_non_empty_fields_if_jonurnal_title_present():
    schema = PublicationInfoItemSchemaV1()
    dump = {
        'journal_title': 'Test JT',
        'journal_volume': 'Test JV',
    }
    expected = {
        'journal_title': 'Test JT',
        'journal_volume': 'Test JV',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_non_empty_fields_if_pubinfo_freetext_present():
    schema = PublicationInfoItemSchemaV1()
    dump = {
        'pubinfo_freetext': 'Test PubInfoFreetext',
    }
    expected = {
        'pubinfo_freetext': 'Test PubInfoFreetext',
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)
