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

from inspirehep.modules.records.serializers.schemas.json.literature.common import AcceleratorExperimentSchemaV1


def test_returns_legacy_name_as_name():
    schema = AcceleratorExperimentSchemaV1()
    dump = {'legacy_name': 'Test'}
    expected = {'name': 'Test'}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_dashed_institution_accelerator_experiment_as_name_if_all_present():
    schema = AcceleratorExperimentSchemaV1()
    dump = {
        'legacy_name': 'LEGACY-EXP1',
        'institutions': [{'value': 'INS'}],
        'accelerator': {'value': 'ACC'},
        'experiment': {'value': 'EXP1'},
    }
    expected = {
        'name': 'INS-ACC-EXP1'
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_legacy_name_as_name_if_accelerator_missing():
    schema = AcceleratorExperimentSchemaV1()
    dump = {
        'legacy_name': 'LEGACY-EXP1',
        'institutions': [{'value': 'INS'}],
        'experiment': {'value': 'EXP1'},
    }
    expected = {
        'name': 'LEGACY-EXP1'
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_legacy_name_as_name_if_institutions_missing():
    schema = AcceleratorExperimentSchemaV1()
    dump = {
        'legacy_name': 'LEGACY-EXP1',
        'accelerator': {'value': 'ACC'},
        'experiment': {'value': 'EXP1'},
    }
    expected = {
        'name': 'LEGACY-EXP1'
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_legacy_name_as_name_if_experiment_missing():
    schema = AcceleratorExperimentSchemaV1()
    dump = {
        'legacy_name': 'LEGACY-EXP1',
        'institutions': [{'value': 'INS'}],
        'accelerator': {'value': 'ACC'},
    }
    expected = {
        'name': 'LEGACY-EXP1'
    }

    result = schema.dumps(dump).data

    assert expected == json.loads(result)


def test_returns_none_as_name_if_empty_present():
    schema = AcceleratorExperimentSchemaV1()
    dump = {}
    expected = {'name': None}

    result = schema.dumps(dump).data

    assert expected == json.loads(result)
