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

import mock
import os
import pkg_resources

from inspire_schemas.api import load_schema, validate
from inspirehep.modules.workflows.tasks.refextract import (
    extract_journal_info,
    extract_references_from_pdf,
    extract_references_from_text,
    raw_refs_to_list,

)
from inspirehep.utils.references import map_refextract_reference_to_schema, \
    map_refextract_to_schema

from mocks import MockEng, MockObj


@mock.patch('inspirehep.modules.workflows.tasks.refextract.create_journal_kb_dict')
def test_extract_journal_info(mock_create_journal_kb_dict):
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)'},
        ],
    }
    extra_data = {}
    assert validate(data['publication_info'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert extract_journal_info(obj, eng) is None

    expected = [
        {
            'artid': '082102',
            'journal_title': 'J. Math. Phys.',
            'journal_volume': '55',
            'pubinfo_freetext': 'J. Math. Phys. 55, 082102 (2014)',
            'year': 2014,
        }
    ]
    result = obj.data['publication_info']

    assert validate(result, subschema) is None
    assert expected == result


@mock.patch('inspirehep.modules.workflows.tasks.refextract.create_journal_kb_dict')
def test_extract_journal_info_handles_year_an_empty_string(mock_create_journal_kb_dict):
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {
                'pubinfo_freetext': 'The Astrophysical Journal, 838:134 (16pp), 2017 April 1'
            },
        ],
    }
    extra_data = {}
    assert validate(data['publication_info'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert extract_journal_info(obj, eng) is None

    expected = [
        {
            'artid': '134',
            'journal_title': 'Astrophys. J.',
            'journal_volume': '838',
            'page_start': '134',
            'pubinfo_freetext': 'The Astrophysical Journal, 838:134 (16pp), 2017 April 1',
        },
    ]
    result = obj.data['publication_info']

    assert validate(result, subschema) is None
    assert expected == result


@mock.patch('inspirehep.modules.workflows.tasks.refextract.create_journal_kb_dict')
def test_extract_journal_info_handles_the_journal_split(mock_create_journal_kb_dict):
    schema = load_schema('hep')
    subschema = schema['properties']['publication_info']

    data = {
        'publication_info': [
            {'pubinfo_freetext': 'Phys. Rev. D 96, 076008. 2017'},
        ],
    }
    extra_data = {}
    assert validate(data['publication_info'], subschema) is None

    obj = MockObj(data, extra_data)
    eng = MockEng()

    assert extract_journal_info(obj, eng) is None

    expected = [
        {
            'artid': '076008',
            'journal_title': 'Phys. Rev. D',
            'journal_volume': '96',
            'pubinfo_freetext': 'Phys. Rev. D 96, 076008. 2017',
        },
    ]
    result = obj.data['publication_info']

    assert validate(result, subschema) is None
    assert expected == result


def test_extract_references_from_pdf_handles_unicode():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1704.00452.pdf'))

    result = extract_references_from_pdf(filename)

    assert validate(result, subschema) is None
    assert len(result) > 0


def test_extract_references_doesnt_raise_exception_if_dealing_with_xml():
    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', 'PhysRevA_104.012407.xml'))

    result = extract_references_from_pdf(filename)

    assert result == []


def test_extract_references_from_pdf_populates_raw_refs_source():
    filename = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', '1704.00452.pdf'))

    result = extract_references_from_pdf(filename, source='arXiv')

    assert result[0]['raw_refs'][0]['source'] == 'arXiv'


def test_extract_references_from_text_handles_unicode():
    schema = load_schema('hep')
    subschema = schema['properties']['references']
    text = u'Iskra Ł W et al 2017 Acta Phys. Pol. B 48 581'

    result = extract_references_from_text(text)

    assert validate(result, subschema) is None
    assert len(result) > 0


def test_refextract_references_from_text_removes_duplicate_urls():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    text = u'[4] CALICE Collaboration webpage. http://twiki.cern.ch/CALICE hello http://twiki.cern.ch/CALICE'
    result = extract_references_from_text(text)

    assert validate(result, subschema) is None
    assert len(result[0]['reference']['urls']) == 1


def test_extract_references_from_text_populates_raw_refs_source():
    text = u'Iskra Ł W et al 2017 Acta Phys. Pol. B 48 581'

    result = extract_references_from_text(text, source='submitter')

    assert result[0]['raw_refs'][0]['source'] == 'submitter'


def test_raw_refs_to_list_single_text():
    reference = {
        'raw_refs': [
            {
                'schema': 'text',
                'source': 'arXiv',
                'value': '[37] M. Vallisneri, \u201cUse and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects,\u201d Phys. Rev. D 77, 042001 (2008) doi:10.1103/PhysRevD.77.042001 [gr-qc/0703086 [GR-QC]].'
            },
        ],
    }

    raw_refs, _ = raw_refs_to_list([reference])
    assert len(raw_refs["values"]) == 1
    assert raw_refs["values"][0] == reference['raw_refs'][0]["value"]


def test_map_refextract_to_schema():
    result = map_refextract_to_schema([
        {
            "author": [
                "Pol. B"
            ],
            "misc": ["Iskra \Ł W et alActa Phys",
                     "48 581"],
            "raw_ref": ["Iskra \Ł W et al 2017 Acta Phys. Pol. B 48 581"
                        ],
            "year": [
                "2017"
            ]
        },
        {
            "author": [
                "Pol. B"
            ],
            "misc": ["Iskra \Ł W et alActa Phys",
                     "48 582"
                     ],
            "raw_ref": ["Iskra \Ł W et al 2017 Acta Phys. Pol. B 48 582"
                        ],
            "year": [
                "2017"
            ]
        }], "elsevier")

    assert result[0]["raw_refs"] == [{'schema': 'text', 'source': 'elsevier',
                                      'value': 'Iskra \\\xc5\x81 W et al 2017 Acta Phys. Pol. B 48 581'}]
    assert result[0]["reference"] == {'authors': [{'full_name': 'B, Pol.'}],
                                      'misc': ['Iskra \\\xc5\x81 W et alActa Phys',
                                               '48 581'],
                                      'publication_info': {'year': 2017}}
    assert result[1]["raw_refs"] == [{'schema': 'text', 'source': 'elsevier',
                                      'value': 'Iskra \\\xc5\x81 W et al 2017 Acta Phys. Pol. B 48 582'}]
    assert result[1]["reference"] == {'authors': [{'full_name': 'B, Pol.'}],
                                      'misc': ['Iskra \\\xc5\x81 W et alActa Phys',
                                               '48 582'],
                                      'publication_info': {'year': 2017}}


def test_map_refextract_reference_to_schema():
    result = map_refextract_reference_to_schema({
        "author": [
            "Pol. B"
        ],
        "misc": ["Iskra \Ł W et alActa Phys",
                 "48 581"
                 ],
        "raw_ref": ["Iskra \Ł W et al 2017 Acta Phys. Pol. B 48 581"
                    ],
        "year": [
            "2017"
        ]
    }, "elsevier")

    assert result[0]["raw_refs"] == [{'schema': 'text', 'source': 'elsevier',
                                      'value': 'Iskra \\\xc5\x81 W et al 2017 Acta Phys. Pol. B 48 581'}]
    assert result[0]["reference"] == {'authors': [{'full_name': 'B, Pol.'}],
                                      'misc': ['Iskra \\\xc5\x81 W et alActa Phys',
                                               '48 581'],
                                      'publication_info': {'year': 2017}}


def test_raw_refs_to_list_multiple_text_takes_first():
    reference = {
        'raw_refs': [
            {
                'schema': 'text',
                'source': 'arXiv',
                'value': '[37] M. Vallisneri, \u201cUse and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects,\u201d Phys. Rev. D 77, 042001 (2008) doi:10.1103/PhysRevD.77.042001 [gr-qc/0703086 [GR-QC]].'
            },
            {
                'schema': 'text',
                'source': 'somewhere',
                'value': 'Some other content'
            }
        ],
    }

    raw_refs, _ = raw_refs_to_list([reference])

    assert len(raw_refs["values"]) == 1
    assert raw_refs["values"][0] == reference['raw_refs'][0]["value"]
    assert raw_refs["sources"][0] == reference['raw_refs'][0]["source"]


def test_raw_refs_to_list_wrong_schema():
    reference = {
        'raw_refs': [
            {
                'source': 'American Physical Society',
                'value': (
                    '<ref id="c1"><label>[1]</label><mixed-citation publication-type="journal"><object-id>1</object-id><person-group'
                    'person-group-type="author"><string-name>Z. Chacko</string-name>, <string-name>H.-S.'
                    'Goh</string-name>, and <string-name>R. Harnik</string-name></person-group>,'
                    '<article-title>The Twin Higgs: Natural Electroweak Breaking from Mirror Symmetry</article-title>,'
                    '<source>Phys. Rev. Lett.</source> <volume>96</volume>, <page-range>231802</page-range>'
                    '(<year>2006</year>).<pub-id pub-id-type="coden">PRLTAO</pub-id><issn>0031-9007</issn><pub-id'
                    'pub-id-type="doi" specific-use="suppress-display">10.1103/PhysRevLett.96.231802</pub-id></mixed-citation></ref>'
                ),
                'schema': 'JATS',
            },
        ],
    }

    raw_refs, _ = raw_refs_to_list([reference])
    assert len(raw_refs["values"]) == 0


def test_raw_refs_to_list_reference_exists():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    reference = {
        'raw_refs': [
            {
                'schema': 'text',
                'source': 'arXiv',
                'value': '[37] M. Vallisneri, \u201cUse and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects,\u201d Phys. Rev. D 77, 042001 (2008) doi:10.1103/PhysRevD.77.042001 [gr-qc/0703086 [GR-QC]].'
            },
        ],
        'reference': {
            'arxiv_eprint': 'gr-qc/0703086',
            'authors': [
                {
                    'full_name': 'Vallisneri, M.'
                }
            ],
            'dois': [
                '10.1103/PhysRevD.77.042001'
            ],
            'label': '37',
            'misc': [
                'Phys. Rev. D',
                '77, 042001',
                '[GR-QC]]'
            ],
            'publication_info': {
                'year': 2008
            },
            'texkey': 'Vallisneri:2007ev',
            'title': {
                'title': 'Use and abuse of the Fisher information matrix in the assessment of gravitational-wave parameter-estimation prospects'
            }
        }
    }

    _, references = raw_refs_to_list([reference])

    assert validate(references, subschema) is None
    assert len(references) == 1
    assert references[0] == reference
