# This is a test for the actions
import json
import os

from inspirehep.modules.multieditor import actions

schema_1 = {
  "properties": {
      "abstracts": {
        "description": ":MARC: ``520``",
        "items": {
          "additionalProperties": 'false',
          "description": "This is used to add, besides the `value`, the `source`\
                          where this value\ncame from.",
          "properties": {
            "source": {
              "$schema": "http://json-schema.org/schema#",
              "description": "Source of the information in this field.\
                              As several records can be merged,\nthis\
                              information allows us to remember where every\
                              bit of metadata came\nfrom and make\
                              decisions based on it.\n\n:MARC:\
                              Often not present.",
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
        "uniqueItems": 'true'
      }},
  "type": "object",
}
record_1 = {
    "abstracts": [
      {
        "value": "A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$"
                 " of proton-proton collisions at $\\sqrt{s} = 13~\\"
                 "mathrm{TeV}$ was recorded by the CMS experiment at"
                 " the CERN LHC. These data are used to search for new"
                 " light bosons with a mass in the range $0.25-8.5~\\ma"
                 "thrm{GeV}/c^2$ decaying into muon pairs. No excess is"
                 " observed in the data, and a model-independent upper l"
                 "imit on the product of the cross section, branching fra"
                 "ction and acceptance is derived. The results are interp"
                 "reted in the context of two benchmark models, namely, th"
                 "e next-to-minimal supersymmetric"
                 " standard model, and dark"
                 " SUSY models including those predicting a non-negligible"
                 " light boson lifetime."
      }
    ],
}
schema_2 = {
  "properties": {
      "source": {
        "$schema": "http://json-schema.org/schema#",
        "description": "Source of the information in this field. As several\
                        records can be merged,\nthis information\
                        allows us to remember where every bit of\
                        metadata came\nfrom and make decisions based\
                        on it.\n\n:MARC: Often not present.",
        "type": "string"
      }},
  "type": "object",
}


def test_update_array():
    """should test record edit for nested complex array."""
    record = {
        'a': [{'bla': ['val5', 'val4']}, {'bla': ['val1', 'val6']},
              {'bla': ['val2']}, {'bla': ['val3']}], 'b': {'c': {'d': 'pong'}}
    }
    expected_map = {
        'a': [{'bla': ['val5', 'success']}, {'bla': ['val1', 'val6']},
              {'bla': ['val2']}, {'bla': ['val3']}], 'b': {'c': {'d': 'pong'}}
    }
    key = 'a/bla'
    action = 'update'
    values_to_check = ['val4']
    value = 'success'
    assert actions.run_action({}, record, key, action,
                              value, values_to_check,
                              False,
                              '', '') == expected_map


def test_update_multiple_update_array():
    """should test action for nested complex array and multiple check values"""
    record = {
      'a': [{'bla': ['val5', 'val4']}, {'bla': ['val1', 'val4']},
            {'bla': ['val2']}, {'bla': ['val3']}], 'b': {'c': {'d': 'pong'}}
    }
    expected_map = {
      'a': [{'bla': ['success', 'success']}, {'bla': ['val1', 'success']},
            {'bla': ['val2']}, {'bla': ['val3']}], 'b': {'c': {'d': 'pong'}}
    }
    key = 'a/bla'
    action = 'update'
    values_to_check = ['val4', 'val5']
    value = 'success'
    assert actions.run_action({}, record, key, action,
                              value, values_to_check,
                              False,
                              '', '',) == expected_map


def test_addition_array():
    """should test record addition for nested array"""
    record = {
      'a': [{'bla': ['val5', 'val4']},
            {'bla': ['val1', 'val6']},
            {'bla': ['val2']},
            {'bla': ['val3']}],
      'b': {'c': {'d': 'pong'}}
    }
    expected_map = {
      'a': [{'bla': ['val5', 'val4', 'success']},
            {'bla': ['val1', 'val6', 'success']},
            {'bla': ['val2', 'success']},
            {'bla': ['val3', 'success']}],
      'b': {'c': {'d': 'pong'}}
    }
    key = 'a/bla'
    action = 'add'
    values_to_check = []
    value = 'success'
    assert actions.run_action({}, record, key, action,
                              value, values_to_check,
                              False,
                              '', '') == expected_map


def test_deletion_array():
    """should test record deletion for nested array"""
    record = {
      'a': [{'bla': ['val5', 'val4']},
            {'bla': ['val1', 'val6']},
            {'bla': ['val4', 'val6']},
            {'bla': ['val3']}],
      'b': {'c': {'d': 'pong'}}
    }
    expected_map = {
      'a': [{'bla': ['val5', 'val4']},
            {'bla': ['val1']},
            {'bla': ['val4']},
            {'bla': ['val3']}],
      'b': {'c': {'d': 'pong'}}
    }
    key = 'a/bla'
    action = 'delete'
    values_to_check = ['val6']
    value = ''
    assert actions.run_action({}, record, key, action,
                              value, values_to_check,
                              False,
                              '', '') == expected_map


def test_deletion_empty_rec():
    record = {
        'key1': {
            'key2': {
                'key3': 'val'
            }
        }
    }
    key = 'key1/key2/key3'
    action = 'delete'
    expected_map = {}
    assert actions.run_action({}, record, key, action,
                              '', ['val'], False,
                              '', '') == expected_map


def test_field_not_existing():
    """should test sub_record creation for missing object"""
    key = ['abstracts', 'source']
    record = {'abstracts': [{'not_source': 'success'}]}
    expected_map = {'abstracts': [{'not_source': 'success'}]}
    action = 'Update'
    assert actions.run_action({}, record, key, action,
                              'test', ['val'], False,
                              '', '') == expected_map


def test_record_creation():
    """should test sub_record creation for missing object"""
    key = ['abstracts', 'source']
    value = 'success'
    target_object = {'abstracts': [{'source': 'success'}]}
    assert actions.create_schema_record(schema_1, key, value) == target_object


def test_record_creation_2():
    """should test sub_record creation for missing object"""
    key = ['source']
    value = 'success'
    target_object = {'source': 'success'}
    assert actions.create_schema_record(schema_2, key, value) == target_object


def test_record_creation_3():
    """should test sub_record creation for missing object"""
    key = 'abstracts/source'
    value = 'success'
    action = 'add'
    target_object = {
        "abstracts": [
          {
            "value": "A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$"
                     " of proton-proton collisions at $\\sqrt{s} = 13~\\"
                     "mathrm{TeV}$ was recorded by the CMS experiment at"
                     " the CERN LHC. These data are used to search for new"
                     " light bosons with a mass in the range $0.25-8.5~\\ma"
                     "thrm{GeV}/c^2$ decaying into muon pairs. No excess is"
                     " observed in the data, and a model-independent upper l"
                     "imit on the product of the cross section, branching fra"
                     "ction and acceptance is derived. The results are interp"
                     "reted in the context of two benchmark models, namely, th"
                     "e next-to-minimal supersymmetric"
                     " standard model, and dark"
                     " SUSY models including those predicting a non-negligible"
                     " light boson lifetime.",
            'source': 'success'
          },
        ],
    }
    assert actions.run_action(schema_1, record_1, key, action,
                              value, [], False, '',
                              '') == target_object


def test_big_record_update():
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_3.json')) as data_file:
        input_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_3_expected.json'))\
            as data_file:
        expected_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/schema.json'))\
            as data_file:
        schema = json.load(data_file)
    publication_info = {
        "cnum": "Success",
        "journal_title": "Success",
        "journal_volume": "Success",
        "year": 2017
      }
    temp_rec = actions.run_action({}, input_record, 'public_notes/value',
                                  'update', 'Success',
                                  ['*Temporary record*'], False, '', '')
    temp_rec = actions.run_action(schema, temp_rec, 'publication_info',
                                  'add', publication_info,
                                  [], False, '', '')
    temp_rec = actions.run_action(schema, temp_rec, 'texkeys',
                                  'add', 'Success',
                                  [], False, '', '')
    assert actions.run_action(schema, temp_rec,
                              'inspire_categories/source',
                              'delete', {},
                              [], False, 'inspire_categories/term',
                              'Phenomenology-HEP') == expected_record


def test_big_record_where_nested_addition():
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_4.json')) as data_file:
        input_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_4_expected.json'))\
            as data_file:
        expected_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/schema.json'))\
            as data_file:
        schema = json.load(data_file)
    assert actions.run_action(schema, input_record, 'authors/ids',
                              'add', {"value": "Success"},
                              [], False, 'authors/affiliations/value',
                              'INFN, Rome') == expected_record


def test_big_record_update_affiliation():
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_4.json')) as data_file:
        input_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_4_expected.json'))\
            as data_file:
        expected_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/schema.json'))\
            as data_file:
        schema = json.load(data_file)
    assert actions.run_action(schema, input_record, 'authors/ids',
                              'add', {"value": "Success"},
                              [], False, 'authors/affiliations/value',
                              'INFN, Rome') == expected_record


def test_big_record_regex_where():
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_4.json')) as data_file:
        input_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/test_record_4_expected_regex.json'))\
            as data_file:
        expected_record = json.load(data_file)
    with open(os.path.join(curr_path,
                           'fixtures/schema.json'))\
            as data_file:
        schema = json.load(data_file)
    assert actions.run_action(schema, input_record,
                              'authors/affiliations/value',
                              'update', "Success",
                              ['Rome'], True, 'authors/signature_block',
                              'BANARo') == expected_record
