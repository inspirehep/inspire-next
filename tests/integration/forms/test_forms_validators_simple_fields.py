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

import pytest
from wtforms.validators import ValidationError

from inspirehep.modules.forms.validators.simple_fields import (
    duplicated_arxiv_id_validator,
    duplicated_doi_validator,
)

from utils import _create_record, _delete_record


class MockField(object):
    def __init__(self, data):
        self.data = data


@pytest.fixture(scope='function')
def deleted_record(app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th'
                ],
                'value': '1607.12345'
            }
        ],
        'control_number': 111,
        'deleted': True,
        'document_type': [
            'article',
        ],
        'dois': [
            {
                'value': '10.1234/PhysRevD.94.054021'
            }
        ],
        'titles': [
            {'title': 'deleted'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        },
        '_collections': ['Literature']
    }

    _create_record(record)

    yield record

    _delete_record('lit', 111)


@pytest.fixture(scope='function')
def normal_record(app):
    record = {
        '$schema': 'http://localhost:5000/schemas/records/hep.json',
        'arxiv_eprints': [
            {
                'categories': [
                    'hep-th'
                ],
                'value': '1607.12345'
            }
        ],
        'control_number': 111,
        'document_type': [
            'article',
        ],
        'dois': [
            {
                'value': '10.1234/PhysRevD.94.054021'
            }
        ],
        'titles': [
            {'title': 'deleted'},
        ],
        'self': {
            '$ref': 'http://localhost:5000/schemas/records/hep.json',
        },
        '_collections': ['Literature']
    }

    _create_record(record)

    yield record

    _delete_record('lit', 111)


def test_existing_arxiv_id_deleted_record_does_not_fail(deleted_record):
    duplicated_arxiv_id_validator(
        None,
        MockField(deleted_record['arxiv_eprints'][0]['value']),
    )


def test_existing_doi_deleted_record_does_not_fail(deleted_record):
    duplicated_doi_validator(
        None,
        MockField(deleted_record['dois'][0]['value']),
    )


def test_existing_arxiv_id_record_does_fail(normal_record):
    with pytest.raises(ValidationError):
        duplicated_arxiv_id_validator(
            None,
            MockField(normal_record['arxiv_eprints'][0]['value']),
        )


def test_existing_doi_record_does_fail(normal_record):
    with pytest.raises(ValidationError):
        duplicated_doi_validator(
            None,
            MockField(normal_record['dois'][0]['value']),
        )
