# -*- coding: utf-8 -*- #
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

from inspirehep.dojson.utils.geo import (
    match_country_name_to_its_code,
    parse_conference_address,
    parse_institution_address,
)


# TODO: test match_country_code


def test_match_country_name_to_its_code_fetches_from_country_to_iso_code():
    expected = 'AF'
    result = match_country_name_to_its_code('AFGHANISTAN')

    assert expected == result


def test_match_country_name_to_its_code_ignores_case():
    expected = 'AL'
    result = match_country_name_to_its_code('Albania')

    assert expected == result


def test_match_country_name_to_its_code_uses_alternative_spellings():
    expected = 'AM'
    result = match_country_name_to_its_code('Republic of Armenia')

    assert expected == result


def test_match_country_name_disambiguates_koreas_when_given_a_city():
    expected = 'KR'
    result = match_country_name_to_its_code('Korea', city='Seoul')

    assert expected == result


def test_match_country_name_doesnt_crash_when_disambiguating_koreas():
    assert match_country_name_to_its_code('Korea') is None


# TODO: test match_us_state


def test_parse_conference_address_recognizes_state_and_country_of_us_city():
    expected = {
        'city': None,
        'country_code': 'US',
        'latitude': None,
        'longitude': None,
        'original_address': 'Waltham, Mass.',
        'state': 'US-MA',
    }
    result = parse_conference_address('Waltham, Mass.')

    assert expected == result


def test_parse_conference_address_recognizes_country_of_non_us_city():
    expected = {
        'city': None,
        'country_code': 'SU',
        'latitude': None,
        'longitude': None,
        'original_address': 'Dubna, USSR',
        'state': None,
    }
    result = parse_conference_address('Dubna, USSR')

    assert expected == result


def test_parse_conference_address_handles_empty_string():
    expected = {
        'city': None,
        'country_code': None,
        'latitude': None,
        'longitude': None,
        'original_address': '',
        'state': None,
    }
    result = parse_conference_address('')

    assert expected == result


def test_parse_institution_address_adds_country_code():
    address = {
        'address': None,
        'city': 'Beijing',
        'state_province': None,
        'country': 'China',
        'postal_code': '123-CFG',
        'country_code': None,
    }

    expected = {
        'city': 'Beijing',
        'country_code': 'CN',
        'original_address': '',
        'postal_code': '123-CFG',
        'state': None,
    }
    result = parse_institution_address(**address)

    assert expected == result


def test_parse_institution_address_preserves_the_original_address():
    address = {
        'address': 'Tuscaloosa, AL 35487-0324',
        'city': 'Tuscaloosa',
        'country': '',
        'state_province': 'AL',
        'postal_code': 'PO Box 870324',
        'country_code': None,
    }

    expected = {
        'city': 'Tuscaloosa',
        'country_code': 'US',
        'original_address': 'Tuscaloosa, AL 35487-0324',
        'postal_code': 'PO Box 870324',
        'state': 'US-AL',
    }
    result = parse_institution_address(**address)

    assert expected == result


def test_parse_institution_address_handles_state_province_none():
    address = {
        'address': None,
        'city': 'Beijing',
        'state_province': None,
        'country': None,
        'postal_code': '123-CFG',
        'country_code': None,
    }

    expected = {
        'city': 'Beijing',
        'country_code': None,
        'original_address': '',
        'postal_code': '123-CFG',
        'state': None,
    }
    result = parse_institution_address(**address)

    assert expected == result
