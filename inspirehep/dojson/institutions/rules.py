# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016, 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON rules for Institutions."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils

from inspirehep.utils.helpers import force_force_list

from .model import institutions
from ..utils import force_single_element, get_record_ref
from ..utils.geo import parse_institution_address


ACRONYM = re.compile(r'\s*\((.*)\)\s*$')


@institutions.over('location', '^034..')
def location(self, key, value):
    def _get_float(value, c):
        try:
            return float(value[c])
        except (TypeError, KeyError, ValueError):
            return ''

    latitude = _get_float(value, 'f')
    longitude = _get_float(value, 'd')

    if latitude and longitude:
        return {
            'latitude': latitude,
            'longitude': longitude,
        }


@institutions.over('external_system_identifiers', '^035..')
@utils.for_each_value
def external_system_identifiers(self, key, value):
    return {
        'schema': force_single_element(value.get('9')),
        'value': force_single_element(value.get('a')),
    }


@institutions.over('ICN', '^110..')
def ICN(self, key, value):
    def _split_acronym(value):
        try:
            acronym = ACRONYM.search(value).group(1)
        except AttributeError:
            acronym = None

        return ACRONYM.sub('', value), acronym

    ICN = self.get('ICN', [])
    legacy_ICN = self.get('legacy_ICN')

    department = self.get('department', [])
    department_acronym = self.get('department_acronym')

    institution = self.get('institution', [])
    institution_acronym = self.get('institution_acronym')

    related_institutes = self.get('related_institutes', [])

    for value in force_force_list(value):
        a_values = force_force_list(value.get('a'))
        if a_values and not institution_acronym:
            a_values[0], institution_acronym = _split_acronym(a_values[0])
        institution.extend(a_values)

        b_values = force_force_list(value.get('b'))
        if b_values and not department_acronym:
            b_values[0], department_acronym = _split_acronym(b_values[0])
        department.extend(b_values)

        ICN.extend(force_force_list(value.get('t')))

        if not legacy_ICN:
            legacy_ICN = force_single_element(value.get('u'))

        x_values = force_force_list(value.get('x'))
        z_values = force_force_list(value.get('z'))
        if len(x_values) == len(z_values):
            for icn, recid in zip(x_values, z_values):
                related_institutes.append({
                    'curated_relation': True,
                    'name': icn,
                    'record': get_record_ref(recid, 'institutions'),
                    'relation_type': 'superseded',
                })
        else:
            for icn in x_values:
                related_institutes.append({
                    'curated_relation': False,
                    'name': icn,
                    'relation_type': 'superseded',
                })

    self['related_institutes'] = related_institutes

    self['institution'] = institution
    self['institution_acronym'] = institution_acronym

    self['department'] = department
    self['department_acronym'] = department_acronym

    self['legacy_ICN'] = legacy_ICN
    return ICN


@institutions.over('address', '^371..')
@utils.for_each_value
def address(self, key, value):
    return parse_institution_address(
        value.get('a'),
        value.get('b'),
        value.get('c'),
        value.get('d'),
        value.get('e'),
        force_force_list(value.get('g')),
    )


@institutions.over('field_activity', '^372..')
@utils.for_each_value
def field_activity(self, key, value):
    FIELD_ACTIVITIES_MAP = {
        'Company': 'Company',
        'Research center': 'Research Center',
        'Research Center': 'Research Center',
        'Research center/': 'Research Center',
        'Research Center-microelectronics': 'Research Center',
        'university': 'University',
        'Univesity': 'University',
        'University': 'University',
    }

    _field_activity = force_single_element(value.get('a'))
    field_activity = FIELD_ACTIVITIES_MAP.get(_field_activity, 'Other')

    return field_activity


@institutions.over('name_variants', '^410..')
def name_variants(self, key, value):
    valid_sources = [
        'DESY_AFF',
        'ADS',
        'INSPIRE'
    ]

    if value.get('9') and value.get('9') not in valid_sources:
        return self.get('name_variants', [])

    if value.get('g'):
        self.setdefault('extra_words', [])
        self['extra_words'].extend(force_force_list(value.get('g')))

    name_variants = self.get('name_variants', [])

    source = force_single_element(value.get('9'))
    for name_variant in force_force_list(value.get('a')):
        name_variants.append({
            'source': source,
            'value': name_variant,
        })

    return name_variants


@institutions.over('related_institutes', '^510..')
@utils.for_each_value
def related_institutes(self, key, value):
    def _classify_relation_type(c):
        if c == 'a':
            return 'predecessor'
        elif c == 'b':
            return 'successor'
        elif c == 't':
            return 'parent'
        elif c == 'r':
            return 'other'
        else:
            return ''

    return {
        'curated_relation': bool(value.get('0')),
        'name': value.get('a'),
        'relation_type': _classify_relation_type(value.get('w')),
        'record': get_record_ref(value.get('0'), endpoint='institutions'),
    }


@institutions.over('historical_data', '^6781.')
def historical_data(self, key, value):
    values = self.get('historical_data', [])
    values.extend(el for el in force_force_list(value.get('a')))

    return values


@institutions.over('core', '^690C.')
def core(self, key, value):
    return value.get('a', '').upper() == 'CORE'
