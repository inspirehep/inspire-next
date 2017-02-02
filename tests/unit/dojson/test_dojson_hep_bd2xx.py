# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_titles_from_245__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="245" ind1=" " ind2=" ">'
        '  <subfield code="a">Exact Form of Boundary Operators Dual to '
        'Interacting Bulk Scalar Fields in the AdS/CFT Correspondence</subfield>'
        '  <subfield code="9">arXiv</subfield>'
        '</datafield>'
    )  # record/001511698

    expected = [
        {
            'title': 'Exact Form of Boundary Operators Dual to Interacting '
                     'Bulk Scalar Fields in the AdS/CFT Correspondence',
            'source': 'arXiv',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']

    expected = [
        {
            'a': 'Exact Form of Boundary Operators Dual to Interacting '
                 'Bulk Scalar Fields in the AdS/CFT Correspondence',
            '9': 'arXiv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['245']


def test_titles_from_246__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="246" ind1=" " ind2=" ">'
        '  <subfield code="a">Superintegrable relativistic systems in'
        ' spacetime-dependent background fields</subfield>'
        '  <subfield code="9">arXiv</subfield>'
        '</datafield>'
    )  # record/1511471

    expected = [
        {
            'source': 'arXiv',
            'title': 'Superintegrable relativistic systems in '
                     'spacetime-dependent background fields',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']

    expected = [
        {
            'a': 'Superintegrable relativistic systems in spacetime-dependent background fields',
            '9': 'arXiv',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['245']


def test_titles_from_245__a_b():
    schema = load_schema('hep')
    subschema = schema['properties']['titles']

    snippet = (
        '<datafield tag="245" ind1=" " ind2=" ">'
        '  <subfield code="a">Proceedings, New Observables in Quarkonium Production</subfield>'
        '  <subfield code="b">Trento, Italy</subfield>'
        '</datafield>'
    )  # record/1510141

    expected = [
        {
            'title': 'Proceedings, New Observables in Quarkonium Production',
            'subtitle': 'Trento, Italy',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['titles'], subschema) is None
    assert expected == result['titles']

    expected = [
        {
            'a': 'Proceedings, New Observables in Quarkonium Production',
            'b': 'Trento, Italy',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['245']
