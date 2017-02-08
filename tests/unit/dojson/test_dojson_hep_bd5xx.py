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

import pytest

from dojson.contrib.marc21.utils import create_record

from inspire_schemas.utils import load_schema
from inspirehep.dojson.hep import hep, hep2marc
from inspirehep.dojson.utils import validate


def test_public_notes_from_500__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">5 pages</subfield>'
        '</datafield>'
    )  # record/1450044

    expected = [
        {
            'source': 'arXiv',
            'value': '5 pages',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {
            '9': 'arXiv',
            'a': '5 pages',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_public_notes_from_500__double_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<datafield tag="500" ind1=" " ind2=" ">'
        '  <subfield code="9">arXiv</subfield>'
        '  <subfield code="a">11 pages, 8 figures. Submitted to MNRAS</subfield>'
        '  <subfield code="a">preliminary entry</subfield>'
        '</datafield>'
    )  # record/1380257

    expected = [
        {
            'source': 'arXiv',
            'value': '11 pages, 8 figures. Submitted to MNRAS',
        },
        {
            'source': 'arXiv',
            'value': 'preliminary entry',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {
            '9': 'arXiv',
            'a': '11 pages, 8 figures. Submitted to MNRAS',
        },
        {
            '9': 'arXiv',
            'a': 'preliminary entry',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_public_notes_from_500__a_and_500__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['public_notes']

    snippet = (
        '<record>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">*Brief entry*</subfield>'
        '  </datafield>'
        '  <datafield tag="500" ind1=" " ind2=" ">'
        '    <subfield code="a">11 pages, 5 figures</subfield>'
        '    <subfield code="9">arXiv</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1450045

    expected = [
        {
            'value': '*Brief entry*',
        },
        {
            'source': 'arXiv',
            'value': '11 pages, 5 figures',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['public_notes'], subschema) is None
    assert expected == result['public_notes']

    expected = [
        {
            'a': '*Brief entry*',
        },
        {
            '9': 'arXiv',
            'a': '11 pages, 5 figures',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['500']


def test_thesis_from_502__a_c_d_z():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (
        '<datafield tag="502" ind1=" " ind2=" ">'
        '  <subfield code="a">PhD</subfield>'
        '  <subfield code="c">IIT, Roorkee</subfield>'
        '  <subfield code="d">2011</subfield>'
        '  <subfield code="z">909554</subfield>'
        '</datafield>'
    )  # record/897773/export/xme

    expected = {
        'date': '2011',
        'defense_date': 'PhD',  # XXX: obviously wrong.
        'institutions': [
            {
                'curated_relation': True,
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/909554',
                },
                'name': 'IIT, Roorkee',
            },
        ],
    }
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = {
        'a': 'PhD',
        'c': [
            'IIT, Roorkee',
        ],
        'd': '2011',
    }
    result = hep2marc.do(result)

    assert expected == result['502']


def test_thesis_from_502_b_double_c_d_double_z():
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    snippet = (
        '<datafield tag="502" ind1=" " ind2=" ">'
        '  <subfield code="b">Thesis</subfield>'
        '  <subfield code="c">Nice U.</subfield>'
        '  <subfield code="c">Cote d\'Azur Observ., Nice</subfield>'
        '  <subfield code="d">2014</subfield>'
        '  <subfield code="z">903069</subfield>'
        '  <subfield code="z">904125</subfield>'
        '</datafield>'
    )  # record/1385648

    expected = {
        'date': '2014',
        'degree_type': 'other',
        'institutions': [
            {
                'curated_relation': True,
                'name': 'Nice U.',
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/903069',
                },
            },
            {
                'curated_relation': True,
                'name': 'Cote d\'Azur Observ., Nice',
                'record': {
                    '$ref': 'http://localhost:5000/api/institutions/904125',
                },
            },
        ],
    }
    result = hep.do(create_record(snippet))

    assert validate(result['thesis_info'], subschema) is None
    assert expected == result['thesis_info']

    expected = {
        'b': 'other',
        'c': [
            'Nice U.',
            'Cote d\'Azur Observ., Nice',
        ],
        'd': '2014',
    }
    result = hep2marc.do(result)

    assert expected == result['502']


def test_abstracts_from_520__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="9">Springer</subfield>'
        '  <subfield code="a">We study a notion of non-commutative integration, in the spirit of modular spectral triples, for the quantum group SU$_{q}$ (2). In particular we define the non-commutative integral as the residue at the spectral dimension of a zeta function, which is constructed using a Dirac operator and a weight. We consider the Dirac operator introduced by Kaad and Senior and a family of weights depending on two parameters, which are related to the diagonal automorphisms of SU$_{q}$ (2). We show that, after fixing one of the parameters, the non-commutative integral coincides with the Haar state of SU$_{q}$ (2). Moreover we can impose an additional condition on the zeta function, which also fixes the second parameter. For this unique choice the spectral dimension coincides with the classical dimension.</subfield>'
        '</datafield>'
    )  # record/1346798

    expected = [
        {
            'source': 'Springer',
            'value': 'We study a notion of non-commutative integration, in the spirit of modular spectral triples, for the quantum group SU$_{q}$ (2). In particular we define the non-commutative integral as the residue at the spectral dimension of a zeta function, which is constructed using a Dirac operator and a weight. We consider the Dirac operator introduced by Kaad and Senior and a family of weights depending on two parameters, which are related to the diagonal automorphisms of SU$_{q}$ (2). We show that, after fixing one of the parameters, the non-commutative integral coincides with the Haar state of SU$_{q}$ (2). Moreover we can impose an additional condition on the zeta function, which also fixes the second parameter. For this unique choice the spectral dimension coincides with the classical dimension.',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['abstracts'], subschema) is None
    assert expected == result['abstracts']

    expected = [
        {
            '9': 'Springer',
            'a': 'We study a notion of non-commutative integration, in the spirit of modular spectral triples, for the quantum group SU$_{q}$ (2). In particular we define the non-commutative integral as the residue at the spectral dimension of a zeta function, which is constructed using a Dirac operator and a weight. We consider the Dirac operator introduced by Kaad and Senior and a family of weights depending on two parameters, which are related to the diagonal automorphisms of SU$_{q}$ (2). We show that, after fixing one of the parameters, the non-commutative integral coincides with the Haar state of SU$_{q}$ (2). Moreover we can impose an additional condition on the zeta function, which also fixes the second parameter. For this unique choice the spectral dimension coincides with the classical dimension.',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['520']


def test_abstracts_from_520__double_a_ignores_second_a():
    schema = load_schema('hep')
    subschema = schema['properties']['abstracts']

    snippet = (
        '<datafield tag="520" ind1=" " ind2=" ">'
        '  <subfield code="a">$D$ $K$ scattering and the $D_s$ spectrum from lattice QCD 520__</subfield>'
        '  <subfield code="a">We present results from Lattice QCD calculations of the low-lying charmed-strange meson spectrum using two types of Clover-Wilson lattices. In addition to quark-antiquark interpolating fields we also consider meson-meson interpolators corresponding to D-meson kaon scattering states. To calculate the all-to-all propagation necessary for the backtracking loops we use the (stochastic) distillation technique. For the charm quark we use the Fermilab method. Results for the $J^P=0^+$ $D_{s0}^*(2317)$ charmed-strange meson are presented.</subfield>'
        '</datafield>'
    )  # record/1297699

    expected = [
        {'value': '$D$ $K$ scattering and the $D_s$ spectrum from lattice QCD 520__'},
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['abstracts'], subschema) is None
    assert expected == result['abstracts']

    expected = [
        {
            'a': '$D$ $K$ scattering and the $D_s$ spectrum from lattice QCD 520__',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['520']


def test_copyright_from_542__d_e_g():
    schema = load_schema('hep')
    subschema = schema['properties']['copyright']

    snippet = (
        '<datafield tag="542" ind1=" " ind2=" ">'
        '  <subfield code="d">American Physical Society</subfield>'
        '  <subfield code="g">2017</subfield>'
        '  <subfield code="e">Article</subfield>'
        '</datafield>'
    )  # record/1511489

    expected = [
        {'holder': 'American Physical Society'},
    ]
    result = hep.do(create_record(snippet))  # no roundtrip

    assert validate(result['copyright'], subschema) is None
    assert expected == result['copyright']

    expected = [
        {'d': 'American Physical Society'},
    ]
    result = hep2marc.do(result)

    assert expected == result['542']


def test_hidden_notes_from_595__a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '  <subfield code="a">Title changed from ALLCAPS</subfield>'
        '</datafield>'
    )  # record/109310

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Title changed from ALLCAPS',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'Title changed from ALLCAPS',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_hidden_notes_from_595__double_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<datafield tag="595" ind1=" " ind2=" ">'
        '  <subfield code="9">SPIRES-HIDDEN</subfield>'
        '  <subfield code="a">TeXtitle from script</subfield>'
        '  <subfield code="a">no affiliation (not clear pn the fulltext)</subfield>'
        '</datafield>'
    )  # record/109310

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'TeXtitle from script',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'TeXtitle from script',
        },
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595']


def test_hidden_notes_from_595__a_9_and_595__double_a_9():
    schema = load_schema('hep')
    subschema = schema['properties']['_private_notes']

    snippet = (
        '<record>'
        '  <datafield tag="595" ind1=" " ind2=" ">'
        '    <subfield code="9">SPIRES-HIDDEN</subfield>'
        '    <subfield code="a">Title changed from ALLCAPS</subfield>'
        '  </datafield>'
        '  <datafield tag="595" ind1=" " ind2=" ">'
        '    <subfield code="9">SPIRES-HIDDEN</subfield>'
        '    <subfield code="a">TeXtitle from script</subfield>'
        '    <subfield code="a">no affiliation (not clear pn the fulltext)</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/109310

    expected = [
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'Title changed from ALLCAPS',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'TeXtitle from script',
        },
        {
            'source': 'SPIRES-HIDDEN',
            'value': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep.do(create_record(snippet))

    assert validate(result['_private_notes'], subschema) is None
    assert expected == result['_private_notes']

    expected = [
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'Title changed from ALLCAPS',
        },
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'TeXtitle from script',
        },
        {
            '9': 'SPIRES-HIDDEN',
            'a': 'no affiliation (not clear pn the fulltext)',
        },
    ]
    result = hep2marc.do(result)

    assert expected == result['595']
