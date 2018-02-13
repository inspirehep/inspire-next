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
# In processing this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function, division

import pytest

from inspire_schemas.api import load_schema
from inspirehep.modules.multieditor.actions import AddProcessor, DeleteProcessor, UpdateProcessor,\
    create_object_from_path


@pytest.fixture
def get_schema():
    return load_schema('hep', resolved=True)


def test_addition_root_key(get_schema):
    """Test adding a root primitive key"""
    subschema = {'type': 'object', 'properties': {'preprint_date': get_schema['properties']['preprint_date']}}
    record = {
    }
    expected_map = {
        'preprint_date': '2016'
    }
    add = AddProcessor(keypath=['preprint_date'], value='2016')
    add.process(record, subschema)
    assert record == expected_map


def test_addition_root_object(get_schema):
    """Test adding a root primitive key"""
    subschema = {'type': 'object', 'properties': {'abstracts': get_schema['properties']['abstracts']}}
    record = {
    }
    expected_map = {
        'abstracts': [
            {
                'source': 'AIP',
                'value': 'Variational principles presented as a logical extension.'
             }
        ]
    }
    object_to_add = {
                'source': 'AIP',
                'value': 'Variational principles presented as a logical extension.'
             }
    add = AddProcessor(keypath=['abstracts'], value=object_to_add)
    add.process(record, subschema)
    assert record == expected_map


def test_addition_missing_root_key(get_schema):
    """Test adding an object with a non allready existing key"""
    subschema = {'type': 'object', 'properties': {'_collections': get_schema['properties']['_collections']}}
    record = {
    }
    expected_map = {
        '_collections': ['Literature']
    }
    add = AddProcessor(keypath=['_collections'], value='Literature',
                       conditions=[{'keypath': ['_collections'], 'match_type':'missing', 'value': ''}])
    add.process(record, subschema)
    assert record == expected_map


def test_addition_missing_deeper_key(get_schema):
    """Test adding an object with condition on a non existing deep key"""
    subschema = {'type': 'object', 'properties': {'public_notes': get_schema['properties']['public_notes']}}
    record = {
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ]
    }
    add = AddProcessor(keypath=['public_notes'], value={'value': 'Preliminary results'},
                       conditions=[{'keypath': ['public_notes', 'value'], 'match_type':'missing', 'value': ''}])
    add.process(record, subschema)
    assert record == expected_map


def test_addition_root_key_with_deeper_condition(get_schema):
    """Test adding a primitive key with multiple deeper conditions"""
    subschema = {'type': 'object', 'properties': {'preprint_date': get_schema['properties']['preprint_date'],
                                                  'core': get_schema['properties']['core'],
                                                  'public_notes': get_schema['properties']['public_notes']}}
    record = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            },
            {
                'value': 'test'
            }
        ],
        'core': True,
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            },
            {
                'value': 'test'
            }
        ],
        'core': True,
        'preprint_date': '2016'
    }
    add = AddProcessor(keypath=['preprint_date'],
                       conditions=[{'keypath': ['public_notes', 'value'], 'value': 'Preliminary results',
                                   'match_type': 'exact'},
                                   {'keypath': ['core'], 'value': 'True', 'match_type': 'exact'}],
                       value='2016')
    add.process(record, subschema)
    assert record == expected_map


def test_addition_root_key_with_deeper_condition_negative(get_schema):
    """Test adding an object with negative condition"""
    subschema = {'type': 'object', 'properties': {'public_notes': get_schema['properties']['public_notes'],
                                                  'core': get_schema['properties']['core'],
                                                  'titles': get_schema['properties']['titles']}}
    record = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test'
            }
        ],
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test'
            }
        ],
    }
    add = AddProcessor(keypath=['preprint_date'],
                       conditions=[{'keypath': ['public_notes', 'value'], 'value': 'Preliminary results',
                                    'match_type': 'exact'},
                                   {'keypath': ['core'], 'value': 'False', 'match_type': 'exact'}],
                       match_type='exact',
                       value='2016')
    add.process(record, subschema)
    assert record == expected_map


def test_addition_object_with_conditions(get_schema):
    """Test adding an object with condition"""
    subschema = {'type': 'object', 'properties': {'public_notes': get_schema['properties']['public_notes'],
                                                  'core': get_schema['properties']['core'],
                                                  'titles': get_schema['properties']['titles']}}
    record = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test'
            }
        ],
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test',
            },
            {
                'title': 'Just another title'
            }
        ],
    }
    add = AddProcessor(keypath=['titles'],
                       conditions=[{'keypath': ['public_notes', 'value'], 'value': 'Preliminary results',
                                    'match_type': 'exact'},
                                   {'keypath': ['core'], 'value': 'True', 'match_type': 'exact'}],
                       value={'title': 'Just another title'})
    add.process(record, subschema)
    assert record == expected_map


def test_addition_object():
    """Test record addition for object"""
    record = {
        'key_a': {
            'key_c': 'test'
        }
    }
    expected_map = {
        'key_a': {
            'key_b': 'Just another title',
            'key_c': 'test'
        }
    }
    custom_schema = {
        'properties': {
            'key_a': {
                'properties': {
                    'key_b': {
                        'type': 'string'
                    },
                    'key_c': {
                        'type': 'string'
                    }
                },
                'required': [
                    'value'
                ],
                'type': 'object'
            },
            'type': 'object',
        },
        'type': 'object',
    }
    add = AddProcessor(keypath=['key_a', 'key_b'], value='Just another title')
    add.process(record, custom_schema)
    assert record == expected_map


def test_addition_array_with_exact_condition():
    """Test record addition for object using condition check"""
    record = {
        'key_a': {
            'key_b': ['Hello'],
            'key_c': 'test'
        }
    }

    expected_map = {
        'key_a': {
            'key_b': ['Hello', 'World'],
            'key_c': 'test'
        }
    }

    custom_schema = {
        'properties': {
            'key_a': {
                'properties': {
                    'key_b': {
                        'items': {
                            'type': 'string'
                        },
                        'type': 'array',
                    },
                    'key_c': {
                        'type': 'string'
                    }
                },
                'required': [
                    'value'
                ],
                'type': 'object'
            },
            'type': 'object',
        },
        'type': 'object',
    }
    add = AddProcessor(keypath=['key_a', 'key_b'],
                       conditions=[{'keypath': ['key_a', 'key_c'],
                                    'match_type': 'exact',
                                    'value':'test'}],
                       value='World')
    add.process(record, custom_schema)
    assert record == expected_map


def test_addition_array(get_schema):
    """Test record addition for field addition in nested array"""
    subschema = {'type': 'object', 'properties': {'titles': get_schema['properties']['titles'],
                                                  'document_type': get_schema['properties']['document_type']}}
    record = {
        'titles': [
            {
                'title': 'test'
            },
            {
                'title': 'test'
            }
        ],
        'document_type': ['book']
    }
    expected_map = {
        'titles': [
            {
                'title': 'test',
                'subtitle': 'Just another title'
            },
            {
                'title': 'test',
                'subtitle': 'Just another title'
            }
        ],
        'document_type': ['book']
    }
    add = AddProcessor(keypath=['titles', 'subtitle'], value='Just another title')
    add.process(record, subschema)
    assert record == expected_map


def test_addition_array_with_contains_condition(get_schema):
    subschema = {'type': 'object', 'properties': {'titles': get_schema['properties']['titles'],
                                                  'document_type': get_schema['properties']['document_type']}}
    record = {
        'titles': [
            {
                'title': 'test_1'
            },
            {
                'title': 'test'
            }
        ],
        'document_type': ['book']
    }
    expected_map = {
        'titles': [
            {
                'title': 'test_1',
                'subtitle': 'Just another title'
            },
            {
                'title': 'test',
                'subtitle': 'Just another title'
            }
        ],
        'document_type': ['book']
    }
    add = AddProcessor(keypath=['titles', 'subtitle'],
                       conditions=[{'keypath': ['titles', 'title'],
                                    'match_type': 'contains',
                                    'value':'test'}],
                       value='Just another title')
    add.process(record, subschema)
    assert record == expected_map


def test_addition_array_with_condition_missing_record():
    record = {}

    expected_map = {}

    custom_schema = {
        'properties': {
            'key_a': {
                'properties': {
                    'key_b': {
                        'items': {
                            'type': 'string'
                        },
                        'type': 'array',
                    },
                    'key_c': {
                        'type': 'string'
                    }
                },
                'required': [
                    'value'
                ],
                'type': 'object'
            },
            'type': 'object',
        },
        'type': 'object',
    }
    add = AddProcessor(keypath=['key_a', 'key_b'],
                       conditions=[{'keypath': ['key_a', 'key_c'],
                                    'match_type': 'exact',
                                    'value':'test'}],
                       value='World')
    add.process(record, custom_schema)
    assert record == expected_map


def test_addition_object_with_condition(get_schema):
    subschema = {'type': 'object', 'properties': {'authors': get_schema['properties']['authors']}}
    record = {
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'Rome'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Rome U.'
                    }
                ],
                'signature_block': 'MANl',
            }
        ]
    }
    expected_map = {
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'Rome'
                    },
                    {
                        'curated_relation': True,
                        'value': 'Just another author'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Rome U.'
                    }
                ],
                'signature_block': 'MANl',
            }
        ]
    }
    add = AddProcessor(keypath=['authors', 'affiliations'],
                       conditions=[{'keypath': ['authors', 'signature_block'],
                                    'match_type': 'exact',
                                    'value':'BANARo'}],
                       value={'curated_relation': True,
                              'value': 'Just another author'})
    add.process(record, subschema)
    assert record == expected_map


def test_deletion_array_to_empty(get_schema):
    """Test record contains deletion for nested array"""
    subschema = {'type': 'object', 'properties': {'texkeys': get_schema['properties']['texkeys'],
                                                  'citeable': get_schema['properties']['citeable']}}
    record = {'texkeys': ['test', 'test', 'test2', 'test'],
              'citeable': True}
    expected_map = {
        'citeable': True
    }

    delete = DeleteProcessor(update_value='test',
                             keypath=['texkeys'],
                             match_type='contains')
    delete.process(record, subschema)
    assert record == expected_map


def test_deletion_array(get_schema):
    """Test record exact deletion for nested array"""
    subschema = {'type': 'object', 'properties': {'texkeys': get_schema['properties']['texkeys'],
                                                  'citeable': get_schema['properties']['citeable']}}
    record = {'texkeys': ['test', 'test', 'test2', 'test'],
              'citeable': True}
    expected_map = {
        'texkeys': ['test2'],
        'citeable': True
    }

    delete = DeleteProcessor(update_value='test',
                             keypath=['texkeys'],
                             match_type='exact')
    delete.process(record, subschema)
    assert record == expected_map


def test_deletion_array_contains(get_schema):
    """Test record deletion for nested array"""
    subschema = {'type': 'object', 'properties': {'inspire_categories': get_schema['properties']['inspire_categories'],
                                                  'citeable': get_schema['properties']['citeable']}}
    record = {'inspire_categories': [{'term': 'Val'},
                                     {'term': 'value'},
                                     {'term': 'value5'}],
              'citeable': True}
    expected_map = {
        'citeable': True
    }

    delete = DeleteProcessor(update_value='val',
                             keypath=['inspire_categories', 'term'],
                             match_type='contains')
    delete.process(record, subschema)
    assert record == expected_map


def test_deletion_array_regex(get_schema):
    """Test record regex deletion for nested array"""
    subschema = {'type': 'object', 'properties': {'inspire_categories': get_schema['properties']['inspire_categories'],
                                                  'citeable': get_schema['properties']['citeable']}}
    record = {'inspire_categories': [{'term': 'val'},
                                     {'term': 'value'},
                                     {'term': 'value5'}],
              'citeable': True}
    expected_map = {
        'citeable': True
    }

    delete = DeleteProcessor(update_value='va.*',
                             keypath=['inspire_categories', 'term'],
                             match_type='regex')
    delete.process(record, subschema)
    assert record == expected_map


def test_deletion_contains(get_schema):
    subschema = {'type': 'object', 'properties': {'inspire_categories': get_schema['properties']['inspire_categories']}}
    record = {'inspire_categories': [{'term': 'val'}]}
    expected_map = {}
    delete = DeleteProcessor(update_value='v',
                             keypath=['inspire_categories', 'term'],
                             match_type='contains')
    delete.process(record, subschema)
    assert record == expected_map


def test_deletion_regex(get_schema):
    subschema = {'type': 'object', 'properties': {'inspire_categories': get_schema['properties']['inspire_categories']}}
    record = {'inspire_categories': [{'term': 'val'}]}
    expected_map = {}
    delete = DeleteProcessor(update_value='v.*',
                             keypath=['inspire_categories', 'term'],
                             match_type='regex')
    delete.process(record, subschema)
    assert record == expected_map


def test_record_creation_root_array(get_schema):
    """Test sub_record creation for missing object"""
    subschema = {'type': 'object', 'properties': {'corporate_author': get_schema['properties']['corporate_author']}}
    key = ['corporate_author']
    value = 'Just another author'
    target_object = {'corporate_author': ['Just another author']}
    assert create_object_from_path(subschema, key, value) == target_object


def test_record_creation_root_object(get_schema):
    """Test sub_record creation for missing object"""
    subschema = {'type': 'object', 'properties': {'self': get_schema['properties']['self']}}
    key = ['self', '$ref']
    value = 'ref_value'
    target_object = {'self': {'$ref': 'ref_value'}}
    assert create_object_from_path(subschema, key, value) == target_object


def test_record_creation():
    """Test sub_record creation for missing object"""
    schema_2 = {
        'properties': {
            'source': {
                'type': 'string'
            }},
        'type': 'object',
    }
    key = ['source']
    value = 'source_value'
    target_object = {'source': 'source_value'}
    assert create_object_from_path(schema_2, key, value) == target_object


def test_record_creation_complex_array(get_schema):
    """Test sub_record creation for missing object"""
    subschema = {'type': 'object', 'properties': {'arxiv_eprints': get_schema['properties']['arxiv_eprints']}}
    key = ['arxiv_eprints', 'categories']
    value = 'astro-ph'
    target_object = {'arxiv_eprints': [{'categories': ['astro-ph']}]}
    assert create_object_from_path(subschema, key, value) == target_object


def test_record_creation_complex(get_schema):
    """Test sub_record creation for missing object"""
    subschema = {'type': 'object', 'properties': {'authors': get_schema['properties']['authors']}}
    key = ['authors', 'affiliations', 'value']
    value = 'affiliation_value'
    target_object = {'authors': [{'affiliations': [{'value': 'affiliation_value'}]}]}
    assert create_object_from_path(subschema, key, value) == target_object


def test_record_creation_array(get_schema):
    """Test sub_record creation for missing object"""
    subschema = {'type': 'object', 'properties': {'authors': get_schema['properties']['authors']}}
    key = ['authors']
    value = {'full_name': 'James Bond'}
    target_object = {'authors': [{'full_name': 'James Bond'}]}
    assert create_object_from_path(subschema, key, value) == target_object


def test_update_regex(get_schema):
    subschema = {'type': 'object', 'properties': {'inspire_categories': get_schema['properties']['inspire_categories']}}
    record = {'inspire_categories': [{'term': 'val'}]}
    expected_map = {'inspire_categories': [{'term': 'term_value'}]}
    update = UpdateProcessor(update_value='v.*',
                             value='term_value',
                             keypath=['inspire_categories', 'term'],
                             match_type='regex')
    update.process(record, subschema)
    assert record == expected_map


def test_update_contains(get_schema):
    subschema = {'type': 'object', 'properties': {'inspire_categories': get_schema['properties']['inspire_categories']}}
    record = {'inspire_categories': [{'term': 'val'}, {'term': 'Val'}]}
    expected_map = {'inspire_categories': [{'term': 'term_value'}, {'term': 'term_value'}]}
    update = UpdateProcessor(update_value='v',
                             value='term_value',
                             keypath=['inspire_categories', 'term'],
                             match_type='contains')
    update.process(record, subschema)
    assert record == expected_map


def test_update_boolean(get_schema):
    subschema = {'type': 'object', 'properties': {'citeable': get_schema['properties']['citeable']}}
    record = {'citeable': True}
    expected_map = {'citeable': False}
    update = UpdateProcessor(update_value='True',
                             value='False',
                             keypath=['citeable'],
                             match_type='exact')
    update.process(record, subschema)
    assert record == expected_map


def test_update_number(get_schema):
    subschema = {'type': 'object', 'properties': {'number_of_pages': get_schema['properties']['number_of_pages']}}
    record = {'number_of_pages': 1984}
    expected_map = {'number_of_pages': 1990}
    update = UpdateProcessor(update_value='1984',
                             value='1990',
                             keypath=['number_of_pages'],
                             match_type='exact')
    update.process(record, subschema)
    assert record == expected_map


def test_record_update_field_not_existing(get_schema):
    """Test sub_record creation for missing object"""
    subschema = {'type': 'object', 'properties': {'abstracts': get_schema['properties']['abstracts']}}
    record = {'abstracts': [{'value': 'abstract_value'}]}
    expected_map = {'abstracts': [{'value': 'abstract_value'}]}
    update = UpdateProcessor(keypath=['abstracts', 'source'],
                             update_value='abstract_value',
                             match_type='exact',
                             value='failure')
    update.process(record, subschema)
    assert record == expected_map


def test_update_array_exact(get_schema):
    """Test record edit for nested complex array."""
    subschema = {'type': 'object', 'properties': {'references': get_schema['properties']['references']}}
    record = {
        'references': [{'reference': {'collaborations': ['Val', 'val4']}},
                       {'reference': {'collaborations': ['val1', 'test val']}}],
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['Val', 'new_value']}},
                       {'reference': {'collaborations': ['val1', 'test val']}}],
    }
    update = UpdateProcessor(update_value='val4',
                             keypath=['references', 'reference', 'collaborations'],
                             match_type='exact',
                             value='new_value')
    update.process(record, subschema)
    assert record == expected_map


def test_update_array_contains(get_schema):
    """Test record edit for nested complex array."""
    subschema = {'type': 'object', 'properties': {'references': get_schema['properties']['references']}}
    record = {
        'references': [{'reference': {'collaborations': ['Val', 'val']}},
                       {'reference': {'collaborations': ['val1', 'test val']}}],
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['collaboration_value', 'collaboration_value']}},
                       {'reference': {'collaborations': ['collaboration_value', 'collaboration_value']}}],
    }
    update = UpdateProcessor(update_value='val',
                             keypath=['references', 'reference', 'collaborations'],
                             match_type='contains',
                             value='collaboration_value')
    update.process(record, subschema)
    assert record == expected_map


def test_update_array_regex(get_schema):
    """Test record edit for nested complex array."""
    subschema = {'type': 'object', 'properties': {'references': get_schema['properties']['references']}}
    record = {
        'references': [{'reference': {'collaborations': ['val5', 'val']}},
                       {'reference': {'collaborations': ['val1', 'val6']}}],
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['collaboration_value', 'collaboration_value']}},
                       {'reference': {'collaborations': ['collaboration_value', 'collaboration_value']}}],
    }
    update = UpdateProcessor(update_value='val.*',
                             keypath=['references', 'reference', 'collaborations'],
                             match_type='regex',
                             value='collaboration_value')
    update.process(record, subschema)
    assert record == expected_map


def test_update_condition_array_regex(get_schema):
    """Test action for nested complex array and multiple check values"""
    subschema = {'type': 'object', 'properties': {'references': get_schema['properties']['references']}}
    record = {
        'references': [{'reference': {'collaborations': ['val5', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['collaboration_value', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }

    update = UpdateProcessor(update_value='val5',
                             keypath=['references', 'reference', 'collaborations'],
                             conditions=[{'keypath': ['references', 'reference', 'title', 'title'],
                                          'match_type': 'regex',
                                          'value':'tes.*'}],
                             match_type='exact',
                             value='collaboration_value')
    update.process(record, subschema)
    assert record == expected_map


def test_update_with_missing_keypath(get_schema):
    """Test sub_record update handling for missing object"""
    subschema = {'type': 'object', 'properties': {'abstracts': get_schema['properties']['abstracts']}}
    record = {
        'abstracts': [
            {
                'value': 'A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$'
            }
        ],
    }
    expected_map = {
        'abstracts': [
            {
                'value': 'A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$'
            },
        ],
    }

    update = UpdateProcessor(update_value='test',
                             keypath=['abstracts', 'source'],
                             value='just a source',
                             match_type='exact')
    update.process(record, subschema)
    assert record == expected_map


def test_update_check_regex_condition(get_schema):
    subschema = {'type': 'object', 'properties': {'authors': get_schema['properties']['authors'],
                                                  'number_of_pages': get_schema['properties']['number_of_pages'],
                                                  'document_type': get_schema['properties']['document_type'],
                                                  'texkeys': get_schema['properties']['texkeys']}}
    record = {
        'document_type': ['book chapter'],
        'texkeys': ['Braendas:1972ts'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'INFN, Rome'
                    },
                    {
                        'value': 'Rome'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {'affiliations': [
                {
                    'value': 'Rome U.'
                },
                {
                    'value': 'Not INF'
                }
            ],
                'signature_block': 'MANl',
            }
        ],
        'number_of_pages': 184
    }
    expected_map = {
        'document_type': ['book chapter'],
        'texkeys': ['Braendas:1972ts'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'an affiliation value'
                    },
                    {
                        'value': 'an affiliation value'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Rome U.'
                    },
                    {
                        'value': 'Not INF'
                    }
                ],
                'signature_block': 'MANl',
            }
        ],
        'number_of_pages': 184
    }
    update = UpdateProcessor(update_value='Rome.*',
                             keypath=['authors', 'affiliations', 'value'],
                             conditions=[{'keypath': ['authors', 'signature_block'],
                                         'match_type':'exact',
                                          'value':'BANARo'},
                                         {'keypath': ['document_type'],
                                         'match_type': 'contains',
                                          'value': 'book'},
                                         {'keypath': ['texkeys'],
                                         'match_type': 'exact',
                                          'value': 'Braendas:1972ts'},
                                         {'keypath': ['number_of_pages'],
                                         'match_type': 'exact',
                                          'value': '184'}
                                         ],
                             match_type='regex',
                             value='an affiliation value')
    update.process(record, subschema)
    assert record == expected_map


def test_update_for_missing_key(get_schema):
    subschema = {'type': 'object', 'properties': {'authors': get_schema['properties']['authors'],
                                                  'document_type': get_schema['properties']['document_type']}}
    record = {
        'document_type': ['book chapter'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'INFN, Rome'
                    },
                    {
                        'value': 'Rome'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {'affiliations': [
                {
                    'value': 'Rome U.'
                },
                {
                    'value': 'Not INF'
                }
            ]
            }
        ]
    }
    expected_map = {
        'document_type': ['book chapter'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'INFN, Rome'
                    },
                    {
                        'value': 'Rome'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'an affiliation value'
                    },
                    {
                        'value': 'Not INF'
                    }
                ]
            }
        ]
    }
    update = UpdateProcessor(update_value='Rome U.',
                             keypath=['authors', 'affiliations', 'value'],
                             conditions=[{'keypath': ['authors', 'signature_block'],
                                         'match_type':'missing',
                                          'value': ''},
                                         {'keypath': ['document_type'],
                                         'match_type': 'regex',
                                          'value': 'book.*'},
                                         ],
                             match_type='exact',
                             value='an affiliation value')
    update.process(record, subschema)
    assert record == expected_map
