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

from inspire_dojson.utils import get_record_ref, validate
from inspire_schemas.utils import load_schema
from inspirehep.modules.references.processors import (
    ReferenceBuilder,
    _is_arxiv,
    _normalize_arxiv,
    _split_refextract_authors_str,
)


def test_split_refextract_authors_str():
    expected = [
        'Butler, D.',
        'Demarque, P.',
        'Smith, H.A.',
    ]
    authors_input = 'D. Butler, P. Demarque, & H. A. Smith'
    result = _split_refextract_authors_str(authors_input)

    assert expected == result


def test_split_refextract_authors_str_discards_et_al():
    expected = [
        'Cenko, S.B.',
        'Kasliwal, M.M.',
        'Perley, D.A.',
    ]
    authors_input = 'S. B. Cenko, M. M. Kasliwal, D. A. Perley et al.'
    result = _split_refextract_authors_str(authors_input)

    assert expected == result


def test_split_refextract_handles_unicode():
    expected = [
        u'Kätlne, J.',
    ]
    result = _split_refextract_authors_str('J. Kätlne et al.')

    assert expected == result


def test_is_arxiv_new_identifier():
    assert _is_arxiv('arXiv:1501.00001v1')


def test_is_arxiv_old_identifier():
    assert _is_arxiv('hep-th/0603001')


def test_normalize_arxiv_handles_new_identifiers_without_prefix_or_version():
    expected = '1501.00001'
    result = _normalize_arxiv('1501.00001')

    assert expected == result


def test_normalize_arxiv_handles_new_identifiers_with_prefix_and_without_version():
    expected = '1501.00001'
    result = _normalize_arxiv('arXiv:1501.00001')

    assert expected == result


def test_normalize_arxiv_handles_new_identifiers_without_prefix_and_with_version():
    expected = '1501.00001'
    result = _normalize_arxiv('1501.00001v1')

    assert expected == result


def test_normalize_arxiv_handles_new_identifiers_with_prefix_and_version():
    expected = '1501.00001'
    result = _normalize_arxiv('arXiv:1501.00001v1')

    assert expected == result


def test_normalize_arxiv_handles_old_identifiers_without_prefix_or_version():
    expected = 'math/0309136'
    result = _normalize_arxiv('math.GT/0309136')

    assert expected == result


def test_normalize_arxiv_handles_old_identifiers_with_prefix_and_without_version():
    expected = 'math/0309136'
    result = _normalize_arxiv('arXiv:math.GT/0309136')

    assert expected == result


def test_normalize_arxiv_handles_old_identifiers_without_prefix_and_with_version():
    expected = 'math/0309136'
    result = _normalize_arxiv('math.GT/0309136v2')

    assert expected == result


def test_normalize_arxiv_handles_old_identifiers_with_prefix_and_version():
    expected = 'math/0309136'
    result = _normalize_arxiv('arXiv:math.GT/0309136v2')

    assert expected == result


def test_normalize_arxiv_handles_solv_int():
    expected = 'solv-int/9611008'
    result = _normalize_arxiv('solv-int/9611008')

    assert expected == result


def test_set_label():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.set_label('Abe et al, 2008')

    expected = [
        {
            'reference': {
                'label': 'Abe et al, 2008',
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_record():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()
    ref = get_record_ref(1226234, 'literature')

    builder.set_record(ref)

    expected = [
        {
            'curated_relation': False,
            'record': {
                '$ref': 'http://localhost:5000/api/literature/1226234',
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_curate():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.curate()

    expected = [
        {'curated_relation': True},
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_texkey():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.set_texkey('Aaij:2016qlz')

    expected = [
        {
            'reference': {
                'texkey': 'Aaij:2016qlz',
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_title():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_title('The CMS experiment at the CERN LHC')

    expected = [
        {
            'reference': {
                'title': {
                    'title': 'The CMS experiment at the CERN LHC',
                }
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_parent_title():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_parent_title('Geom. Funct. Anal., GAFA 2000')

    expected = [
        {
            'reference': {
                'publication_info': {
                    'parent_title': 'Geom. Funct. Anal., GAFA 2000',
                },
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_misc():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_misc('[Erratum:')

    expected = [
        {
            'reference': {
                'misc': [
                    '[Erratum:',
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_raw_reference():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_raw_reference('Phys. Rev. C 80 (doi:10.1103/PhysRevC.80.044313)')

    expected = [
        {
            'raw_refs': [
                {
                    'schema': 'text',
                    'source': '',
                    'value': 'Phys. Rev. C 80 (doi:10.1103/PhysRevC.80.044313)',
                },
            ],
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_year():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.set_year(2017)

    expected = [
        {
            'reference': {
                'publication_info': {
                    'year': 2017,
                },
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_year_rejects_malformed_years():
    builder = ReferenceBuilder()

    builder.set_year('foobar')

    expected = [{}]
    result = [builder.obj]

    assert expected == result


def test_set_year_rejects_invalid_years():
    builder = ReferenceBuilder()

    builder.set_year(666)

    expected = [{}]
    result = [builder.obj]

    assert expected == result

    builder.set_year(2112)

    expected = [{}]
    result = [builder.obj]

    assert expected == result


def test_add_url():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_url('http://www.muonsinc.com')

    expected = [
        {
            'reference': {
                'urls': [
                    {'value': 'http://www.muonsinc.com'},
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_refextract_author_str():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_refextract_authors_str('S. Frixione, P. Nason, and C. Oleari')

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'Frixione, S.'},
                    {'full_name': 'Nason, P.'},
                    {'full_name': 'Oleari, C.'},
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_author():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_author('Cox, Brian')

    expected = [
        {
            'reference': {
                'authors': [
                    {'full_name': 'Cox, Brian'},
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_author_handles_inspire_role():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_author("O'Brian, Dara", 'ed.')

    expected = [
        {
            'reference': {
                'authors': [
                    {
                        'full_name': "O'Brian, Dara",
                        'inspire_role': 'editor',
                    },
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_pubnote():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.set_pubnote('Nucl.Phys.,B360,362')

    expected = [
        {
            'reference': {
                'publication_info': {
                    'artid': '362',
                    'journal_title': 'Nucl.Phys.',
                    'journal_volume': 'B360',
                    'page_start': '362',
                },
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_pubnote_falls_back_to_raw_refs():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.set_pubnote('not-a-valid-pubnote')

    expected = [
        {
            'raw_refs': [
                {
                    'schema': 'text',
                    'source': '',
                    'value': 'not-a-valid-pubnote',
                },
            ],
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_set_publisher():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.set_publisher('Elsevier')

    expected = [
        {
            'reference': {
                'imprint': {
                    'publisher': 'Elsevier',
                },
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_report_number_handles_arxiv_ids():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_report_number('hep-th/0603001')

    expected = [
        {
            'reference': {
                'arxiv_eprint': 'hep-th/0603001',
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_uid_handles_arxiv_ids():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_uid('hep-th/0603001')

    expected = [
        {
            'reference': {
                'arxiv_eprint': 'hep-th/0603001',
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_uid_handles_dois():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_uid('http://dx.doi.org/10.3972/water973.0145.db')

    expected = [
        {
            'reference': {
                'dois': [
                    '10.3972/water973.0145.db',
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_uid_handles_handles():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_uid('hdl:10443/1646')

    expected = [
        {
            'reference': {
                'persistent_identifiers': [
                    {
                        'schema': 'HDL',
                        'value': '10443/1646',
                    },
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_uid_handles_cnums():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_uid('C87-11-11')

    expected = [
        {
            'reference': {
                'publication_info': {
                    'cnum': 'C87-11-11',
                },
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_uid_falls_back_to_isbn():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_uid('1449344852')

    expected = [
        {
            'reference': {
                'isbn': '9781449344856',
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_uid_rejects_invalid_isbns():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_uid('123456789')

    expected = [
        {
            'reference': {
                'misc': [
                    '123456789',
                ]
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result


def test_add_collaboration():
    schema = load_schema('hep')
    subschema = schema['properties']['references']

    builder = ReferenceBuilder()

    builder.add_collaboration('ALICE')

    expected = [
        {
            'reference': {
                'collaborations': [
                    'ALICE',
                ],
            },
        },
    ]
    result = [builder.obj]

    assert validate(result, subschema) is None
    assert expected == result
