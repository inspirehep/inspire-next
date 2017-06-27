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

"""DoJSON rules for Institutions."""

from __future__ import absolute_import, division, print_function

import re

from dojson import utils

from inspirehep.utils.helpers import force_list, maybe_int

from .model import institutions
from ..utils import force_single_element, get_record_ref
from ..utils.geo import parse_institution_address


ACRONYM = re.compile(r'\s*\((.*)\)\s*$')


def _is_secondary_address(value):
    return 'x' in value


def _maybe_float(el):
    try:
        return float(el)
    except (TypeError, ValueError):
        pass


@institutions.over('_location', '^034..')
def _location(self, key, value):
    latitude = _maybe_float(value.get('f'))
    longitude = _maybe_float(value.get('d'))

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
    legacy_ICN = self.get('legacy_ICN', '')
    institution_hierarchy = self.get('institution_hierarchy', [])
    related_records = self.get('related_records', [])

    for value in force_list(value):
        ICN.extend(force_list(value.get('t')))

        if not legacy_ICN:
            legacy_ICN = force_single_element(value.get('u'))

        for b_value in force_list(value.get('b')):
            department_name, department_acronym = _split_acronym(b_value)
            institution_hierarchy.append({
                'acronym': department_acronym,
                'name': department_name,
            })

        for a_value in force_list(value.get('a')):
            institution_name, institution_acronym = _split_acronym(a_value)
            institution_hierarchy.append({
                'acronym': institution_acronym,
                'name': institution_name,
            })

        x_values = force_list(value.get('x'))
        z_values = force_list(value.get('z'))

        # XXX: we zip only when they have the same length, otherwise
        #      we might match a relation with the wrong recid.
        if len(x_values) == len(z_values):
            for _, recid in zip(x_values, z_values):
                related_records.append({
                    'curated_relation': True,
                    'record': get_record_ref(recid, 'institutions'),
                    'relation_freetext': 'obsolete',
                })

    self['related_records'] = related_records
    self['institution_hierarchy'] = institution_hierarchy
    self['legacy_ICN'] = legacy_ICN
    return ICN


@institutions.over('addresses', '^371..')
def addresses_371(self, key, values):
    addresses = self.get('addresses', [])

    for value in force_list(values):
        address = parse_institution_address(
            value.get('a'),
            value.get('b'),
            value.get('c'),
            value.get('d'),
            value.get('e'),
            force_list(value.get('g')),
        )

        if _is_secondary_address(value):
            addresses.append(address)
        else:
            addresses.insert(0, address)

    return addresses


@institutions.over('institution_type', '^372..')
@utils.for_each_value
def institution_type(self, key, value):
    INSTITUTION_TYPE_MAP = {
        'Company': 'Company',
        'Research center': 'Research Center',
        'Research Center': 'Research Center',
        'Research center/': 'Research Center',
        'Research Center-microelectronics': 'Research Center',
        'university': 'University',
        'Univesity': 'University',
        'University': 'University',
    }

    a_value = force_single_element(value.get('a'))
    return INSTITUTION_TYPE_MAP.get(a_value, 'Other')


@institutions.over('name_variants', '^410..')
def name_variants(self, key, value):
    valid_sources = [
        'ADS',
        'INSPIRE'
    ]

    if value.get('9') and value.get('9') not in valid_sources:
        return self.get('name_variants', [])

    if value.get('g'):
        self.setdefault('extra_words', [])
        self['extra_words'].extend(force_list(value.get('g')))

    name_variants = self.get('name_variants', [])

    source = force_single_element(value.get('9'))
    for name_variant in force_list(value.get('a')):
        name_variants.append({
            'source': source,
            'value': name_variant,
        })

    return name_variants


@institutions.over('related_records', '^510..')
@utils.for_each_value
def related_records(self, key, value):
    def _get_relation(value):
        RELATIONS_MAP = {
            'a': 'predecessor',
            'r': 'other',
            't': 'parent',
        }

        return RELATIONS_MAP.get(value.get('w'))

    record = get_record_ref(maybe_int(value.get('0')), 'institutions')
    relation = _get_relation(value)

    if record and relation == 'other':
        return {
            'curated_relation': record is not None,
            'record': record,
            'relation_freetext': relation,
        }
    elif record and relation:
        return {
            'curated_relation': record is not None,
            'record': record,
            'relation': relation,
        }


@institutions.over('historical_data', '^6781.')
@utils.flatten
@utils.for_each_value
def historical_data(self, key, value):
    return force_list(value.get('a'))


@institutions.over('deleted', '^980..')
def deleted(self, key, value):
    deleted = self.get('deleted')
    core = self.get('core')
    inactive = self.get('inactive')

    if not deleted:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        normalized_c_values = [el.upper() for el in force_list(value.get('c'))]
        deleted = 'DELETED' in normalized_a_values or 'DELETED' in normalized_c_values

    if not core:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        core = 'CORE' in normalized_a_values

    if not inactive:
        normalized_a_values = [el.upper() for el in force_list(value.get('a'))]
        normalized_b_values = [el.upper() for el in force_list(value.get('b'))]
        inactive = 'DEAD' in normalized_a_values or 'DEAD' in normalized_b_values

    self['core'] = core
    self['inactive'] = inactive
    return deleted
