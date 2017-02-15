# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Test helpers."""

from inspirehep.modules.records.validators.errors import ValidationError
from inspirehep.modules.recordvalidators.validators.helpers import (
    FIELD_REQUIRE_FIELD_VALUES_TEMPLATE,
    FIELD_VALIDATION_TEMPLATE,
    FIELD_REQUIRE_FIELD_TEMPLATE,
    FIELD_VALUE_REQUIRE_FIELD_TEMPLATE
)
import pytest
from jsonschema import Draft4Validator
from jsonschema.exceptions import ValidationError
from jsonschema.validators import extend, validat
import json


# def test_check_for_author_or_corporate_author_to_exist():
#     sample_record = {
#         'no_authors': {},
#         'no_corporate_author': {}
#     }
#
#     expected = {
#         'globalErrors': [{
#             'message': 'Neither an author nor a corporate author found.',
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_for_author_or_corporate_author_to_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_document_type_if_book_series_exist():
#     sample_record = {
#         'book_series': [{
#             'key': 'value'
#         }],
#         'document_type': ['not_one_of_required_values']
#     }
#     required_values = ['book', 'proceedings', 'thesis']
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
#                             field='book_series',
#                             required='document_type',
#                             values=required_values),
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_document_type_if_book_series_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_document_type_if_isbns_exist():
#     sample_record = {
#         'isbns': [{
#             'key': 'value'
#         }],
#         'document_type': ['not_one_of_required_values']
#     }
#     required_values = ['book', 'proceedings', 'thesis']
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
#                 field='isbns',
#                 required='document_type',
#                 values=required_values),
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_document_type_if_isbns_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_document_type_if_cnum_exist():
#     sample_record = {
#         'publication_info': [{
#             'cnum': 'cnum_value'
#         }],
#         'document_type': ['not_one_of_required_values']
#     }
#     required_values = ['proceedings', 'conference paper']
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
#                 field='cnum',
#                 required='document_type',
#                 values=required_values),
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_document_type_if_cnum_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_document_type_if_thesis_info_exist():
#     sample_record = {
#         'thesis_info': {
#             'key': 'value'
#         },
#         'document_type': ['not_one_of_required_values']
#     }
#     required_values = ['thesis']
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
#                 field='thesis_info',
#                 required='document_type',
#                 values=required_values),
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_document_type_if_thesis_info_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_if_isbn_is_valid():
#     sample_record = {
#         'isbns': [
#             {
#                 'value': '978-3-319-15000-0'
#             },
#             {
#                 'value': '8267411'
#             }
#         ]
#     }
#     expected = {
#         '/isbns/1/value': [{
#             'message': FIELD_VALIDATION_TEMPLATE.format(
#                 field='isbns',
#                 value='8267411'),
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_if_isbn_is_valid(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_date_present_in_record():
#     sample_valid_record = {
#         'thesis_info': {
#             'date': ''
#         }
#     }
#
#     assert check_date_present_in_record(sample_valid_record) == {}
#
#     sample_invalid_record = {
#         'not_date_field': {
#             'not_date_field_key': 'value'
#         }
#     }
#     expected = {
#         'globalErrors': [{
#             'message': 'No date present.',
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_date_present_in_record(sample_invalid_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_languages_if_valid_iso():
#     sample_record = {
#         'languages': [
#             'kr',
#             'z2'
#         ]
#     }
#     expected = {
#         '/languages/1': [{
#             'message': FIELD_VALIDATION_TEMPLATE.format(
#                 field='languages',
#                 value='z2'
#             ),
#             'type': 'Error'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_languages_if_valid_iso(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_affiliations_if_authors_exist():
#     sample_record = {
#         'authors': [
#             {
#                 'not_affiliations_field': []
#             },
#             {
#                 'affiliations': []
#             },
#             {
#                 'affiliations': [{
#                     'key': 'value'
#                 }]
#             }
#         ]
#     }
#     expected = {
#         '/authors/0': [{
#             'message': FIELD_REQUIRE_FIELD_TEMPLATE.format(
#                 field='authors',
#                 required='affiliations'),
#             'type': 'Warning'
#         }],
#         '/authors/1': [{
#             'message': FIELD_REQUIRE_FIELD_TEMPLATE.format(
#                 field='authors',
#                 required='affiliations'),
#             'type': 'Warning'
#         }]
#
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_affiliations_if_authors_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_thesis_info_if_doctype_value_thesis_present():
#     sample_record = {
#         'document_type': [
#             'thesis'
#         ],
#         'not_thesis_info_field': 'value'
#     }
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_VALUE_REQUIRE_FIELD_TEMPLATE.format(
#                 field='document_type',
#                 value='thesis',
#                 required='thesis_info'),
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_thesis_info_if_doctype_value_thesis_present(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_cnum_if_doctype_value_proceedings_present():
#     sample_record = {
#         'document_type': [
#             'proceedings'
#         ],
#         'publication_info': [{
#             'not_cnum_field': 'value'
#         }]
#     }
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_VALUE_REQUIRE_FIELD_TEMPLATE.format(
#                 field='document_type',
#                 value='proceedings',
#                 required='cnum'),
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_cnum_if_doctype_value_proceedings_present(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_cnum_if_doctype_value_conference_paper_present():
#     sample_record = {
#         'document_type': [
#             'conference paper'
#         ],
#         'publication_info': [{
#             'not_cnum_field': 'value'
#         }]
#     }
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_VALUE_REQUIRE_FIELD_TEMPLATE.format(
#                 field='document_type',
#                 value='conference paper',
#                 required='cnum'),
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_cnum_if_doctype_value_conference_paper_present(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_if_2_cnum_exist_in_publication_info():
#     sample_record = {
#         'publication_info': [
#             {
#                 'cnum': 'value'
#             },
#             {
#                 'cnum': 'value'
#             },
#             {
#                 'not_cnum': 'value'
#             }
#         ]
#     }
#     expected = {
#         'globalErrors': [{
#             'message': "2 cnums found in 'publication info' field.",
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_if_2_cnum_exist_in_publication_info(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_doctype_values_if_cnum_present():
#     sample_record = {
#         'publication_info': [{
#                 'cnum': 'value'
#         }],
#         'document_type': [
#             'not_one_of_the_required_values',
#             'another_not_one_of_the_required_values'
#         ]
#     }
#     required_values = ['proceedings', 'conference_paper']
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_REQUIRE_FIELD_VALUES_TEMPLATE.format(
#                 field='cnum',
#                 required='document_type',
#                 values=required_values),
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_doctype_values_if_cnum_present(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_accelerator_experiments_if_collaborations_exist():
#     sample_record = {
#         'collaborations': [{
#             'cnum': 'value'
#         }],
#         'not_accelerator_experiments': []
#     }
#     expected = {
#         'globalErrors': [{
#             'message': FIELD_REQUIRE_FIELD_TEMPLATE.format(
#                 field='collaborations',
#                 required='accelerator_experiments'),
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_accelerator_experiments_if_collaborations_exist(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_accelerator_experiments_for_experiment():
#     sample_record = {
#         'accelerator_experiments': [{
#             'not_experiment_field': 'value'
#         }]
#     }
#     expected = {
#         'globalErrors': [{
#             'message': "'accelerator_experiments' field should have at least "
#                        "one experiment",
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_accelerator_experiments_for_experiment(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_thesis_info_and_supervisor_to_exist_in_thesis():
#     sample_record = {
#         'not_thesis_info': 'value',
#         'inspire_roles': ['not_supervisor'],
#         'document_type': [
#             'thesis'
#         ]
#     }
#     expected = {
#         'globalErrors': [{
#             'message': "Thesis should have both 'thesis_info' and "
#                        "'supervisor' field.",
#             'type': 'Warning'
#         }]
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_thesis_info_and_supervisor_to_exist_in_thesis(sample_record)
#     assert excinfo.value.error == expected
#
#
# def test_check_if_no_pages_for_publication_info():
#     sample_record = {
#         'publication_info': [
#             {
#                 'page_start': 'value'
#             },
#             {
#                 'page_end': 'value'
#             },
#             {
#                 'not_page_start_or_end_field': 'value'
#             },
#             {
#                 'page_start': 'value',
#                 'page_end': 'value'
#             }
#         ]
#     }
#     expected = {
#         '/publication_info/2': [{
#             'message': "Missing 'page_start' or 'page_end' field.",
#             'type': 'Warning'
#         }]
#
#     }
#     with pytest.raises(ValidationError) as excinfo:
#         check_if_no_pages_for_publication_info(sample_record)
#     assert excinfo.value.error == expected

schema = {
    "properties": {
        "authors": {
        "description": ":MARC: ``520``",
        "items": {
            "additionalProperties": False,
            "description": "This is used to add, besides the `value`, the `source` where this value\ncame from.",
            "properties": {
                "source": {
                    "$schema": "http://json-schema.org/schema#",
                    "description": "Source of the information in this field. As several records can be merged,\nthis information allows us to remember where every bit of metadata came\nfrom and make decisions based on it.\n\n:MARC: Often not present.",
                    "type": "string"
                },
                "value": {
                    "type": "string"
                }
            },
            "required": [
                "value"
            ],
            "type": "object"
        },
        "title": "List of abstracts",
        "type": "array",
        "uniqueItems": True
    },
    "corporate_author": {
      "items": {
        "additionalProperties": False,
        "properties": {
          "accelerator": {
            "description": "If present, `institution` should contain the\ninstitution where this accelerator is located.\n\n.. note::\n\n    Currently not used, see `legacy_name`.\n\n:MARC: ``693__a``",
            "type": "string"
          },
          "curated_relation": {
            "default": False,
            "type": "boolean"
          },
          "experiment": {
            "description": "If present, `institution` should contain the\ninstitution where this experiment is located and\n`accelerator` may contain the accelerator that this\nexperiment is using (if appropriate).\n\n.. note::\n\n    Currently not used, see `legacy_name`.\n\n:MARC: not present.",
            "type": "string"
          },
          "institution": {
            "description": ".. note::\n\n    Currently not used, see `legacy_name`.\n\n:MARC: not present.",
            "title": "Institution hosting the experiment",
            "type": "string"
          },
          "legacy_name": {
            "description": "This field is used when migrating from legacy instead\nof separate `institution`, `accelerator` and\n`experiment`. In the future, it will be deprecated and\nthe other fields will be used instead.\n\n:example: ``CERN-LHC-CMS``\n:MARC: ``693__e``",
            "title": "Identifier of the experiment on legacy",
            "type": "string"
          },
          "record": {
            "$schema": "http://json-schema.org/schema#",
            "additionalProperties": False,
            "properties": {
              "$ref": {
                "description": "URL to the referenced resource",
                "format": "url",
                "type": "string"
              }
            },
            "required": [
              "$ref"
            ],
            "title": "Reference to another record",
            "type": "object"
          }
        },
        "type": "object"
      },
      "title": "List of related accelerators/experiments",
      "type": "array",
      "uniqueItems": True
    }
    }
}

record = {
    "abstracts": [
        {
            "source": "arXiv",
            "value": "Holographic RG flows are studied in an Einstein-dilaton theory with a general potential. The superpotential formalism is utilized in order to characterize and classify all solutions that are associated to asymptotically AdS space-times. Such solutions correspond to holographic RG flows and are characterized by their holographic $\\beta$-functions. Novel solutions are found that have exotic properties from a RG point-of view. Some have $\\beta$-functions that are defined patch-wise and lead to flows where the $\\beta$-function changes sign without the flow stopping. Others describe flows that end in non-neighboring extrema in field space. Finally others describe regular flows between two minima of the potential and correspond holographically to flows driven by the VEV of an irrelevant operator in the UV CFT."
        }
    ],
    "accelerator_experiments": [
      {
        "legacy_name": "CERN-LHC-CMS",
        "record": {
          "$ref": "http://localhost:5000/api/experiments/1108642"
        }
      }
    ]
}


def myValidator(validator, value, instance, schema):
    print "Value ", value
    if instance['abstracts']:
        if not len(instance['accelerator_experiments']) == 0:
            yield ValidationError("abstracts field require accelerator_experiments to have one or more values", path=("/abstracts"))


def test_custom_validator():
    custom_validator = extend(Draft4Validator, {'abstracts': myValidator})
    validator = custom_validator(schema["properties"])
    errors = [e for e in validator.iter_errors(record)]
    if len(errors):
        for error in errors:
            print "Err: ", error.path
        assert errors == {}
