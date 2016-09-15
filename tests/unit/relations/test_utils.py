# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function

from inspirehep.modules.relations.utils import extract_element


def test_extract_element_integer():
    record = {
        'outer': {
            'inner': 1196797
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner')] == [1196797]


def test_extract_element_integer_with_must():
    record = {
        'outer': {
            'inner': 1196797
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value'])] == []


def test_extract_element_string():
    record = {
        'outer': {
            'inner': '1196797'
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner')] == ['1196797']


def test_extract_element_string_with_must():
    record = {
        'outer': {
            'inner': '1196797'
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value'])] == []


def test_extract_element_list_of_integers():
    record = {
        'outer': {
            'inner': [1196797, 1234567]
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner')] == [1196797, 1234567]


def test_extract_element_list_of_integers_with_must():
    record = {
        'outer': {
            'inner': [1196797, 1234567]
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value'])] == []


def test_extract_element_list_of_strings():
    record = {
        'outer': {
            'inner': ['1196797', '1234567']
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner')] == ['1196797', '1234567']


def test_extract_element_list_of_strings_with_must():
    record = {
        'outer': {
            'inner': ['1196797', '1234567']
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value'])] == []


def test_extract_element_list_of_dicts():
    record = {
        'outer': {
            'inner': [{'value': 1196797}, {'other_value': 1234567}]
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner')] == [{'value': 1196797},
                                          {'other_value': 1234567}]


def test_extract_element_list_of_dicts_with_present_must():
    record = {
        'outer': {
            'inner': [{'value': 1196797}, {'other_value': 1234567},
                      {'value': 7654321, 'other_value': 5555},
                      {'weird_value': 'WEIRD'}]
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value'])] == [{'value': 1196797},
                                                           {'value': 7654321,
                                                            'other_value': 5555
                                                            }
                                                           ]


def test_extract_element_list_of_dicts_with_two_present_musts():
    record = {
        'outer': {
            'inner': [{'value': 1196797}, {'other_value': 1234567},
                      {'value': 7654321, 'other_value': 5555},
                      {'weird_value': 'WEIRD'}]
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value', 'other_value'])] == [
            {'value': 7654321, 'other_value': 5555}
            ]


def test_extract_element_list_of_dicts_with_non_present_must():
    record = {
        'outer': {
            'inner': [{'value': 1196797}, {'other_value': 1234567},
                      {'value': 7654321, 'other_value': 5555},
                      {'weird_value': 'WEIRD'}]
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['non_value'])] == []


def test_extract_element_dict():
    record = {
        'outer': {
            'inner': {'value': 1196797}
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner')] == [{'value': 1196797}]


def test_extract_element_dict_with_present_must():
    record = {
        'outer': {
            'inner': {'value': 1196797}
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value'])] == [{'value': 1196797}]


def test_extract_element_dict_with_non_present_must():
    record = {
        'outer': {
            'inner': {'value': 1196797}
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['other_value'])] == []


def test_extract_element_dict_with_present_and_non_present_must():
    record = {
        'outer': {
            'inner': {'value': 1196797}
        }
    }
    assert [e for e in extract_element(
        record, field='outer.inner', musts=['value', 'other_value'])] == []


def test_returns_record_itself_when_field_and_must_unspecified():
    record = {
        'outer': {
            'inner': {'value': 1196797}
        }
    }
    assert [e for e in extract_element(record)] == [record]
