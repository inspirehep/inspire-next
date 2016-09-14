# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

"""MARC 21 model definition."""

from __future__ import absolute_import, division, print_function

from dojson import utils

from ..model import institutions
from ...utils import force_single_element, get_record_ref
from ...utils.geo import parse_institution_address

from inspirehep.utils.helpers import force_force_list


@institutions.over('location', '^034..')
def location(self, key, value):
    """GPS location info."""
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


@institutions.over('timezone', '^043..')
@utils.for_each_value
def timezone(self, key, value):
    """Timezone."""
    return value.get('t')


@institutions.over('name', '^110..')
@utils.for_each_value
def name(self, key, value):
    """List of names."""
    def set_value(key, val):
        val = force_force_list(val)
        if val:
            self.setdefault(key, [])
            self[key].extend(val)

    set_value('institution', value.get('a'))
    set_value('department', value.get('b'))
    set_value('ICN', value.get('u'))
    set_value('new_ICN', value.get('t'))

    superseded_icns = force_force_list(value.get('x'))
    superseded_recids = force_force_list(value.get('z'))
    related_institutes = []
    if len(superseded_icns) == len(superseded_recids):
        for icn, recid in zip(superseded_icns, superseded_recids):
            related_institutes.append({
                'curated_relation': True,
                'name': icn,
                'record': get_record_ref(recid, record_type='institutions'),
                'relation_type': 'superseded',
            })
    else:
        for icn in superseded_icns:
            related_institutes.append({
                'curated_relation': False,
                'name': icn,
                'relation_type': 'superseded',
            })
    set_value('related_institutes', related_institutes)

    names = force_force_list(value.get('a'))
    names.extend(force_force_list(value.get('u')))
    names.extend(force_force_list(value.get('t')))
    return names


@institutions.over('address', '^371..')
@utils.for_each_value
def address(self, key, value):
    """Address info."""
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
    """Field of activity."""
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
    """Variants of the name."""
    valid_sources = [
        "DESY_AFF",
        "ADS",
        "INSPIRE"
    ]
    if value.get('9') and value.get('9') not in valid_sources:
        return self.get('name_variants', [])

    if value.get('g'):
        self.setdefault('extra_words', [])
        self['extra_words'].extend(force_force_list(value.get('g')))

    values = self.get('name_variants', [])
    values.append({
        'source': value.get('9'),
        'value': force_force_list(value.get('a', [])),
    })

    return values


@institutions.over('core', '^690C.')
def core(self, key, value):
    """Check if it is a CORE institution."""
    return value.get('a', "").upper() == "CORE"


@institutions.over('non_public_notes', '^667..')
@utils.for_each_value
def non_public_notes(self, key, value):
    """Hidden note."""
    return value.get('a')


@institutions.over('hidden_notes', '^595..')
def hidden_notes(self, key, value):
    """Hidden note."""
    values = self.get('hidden_notes', [])
    values.extend(el for el in force_force_list(value.get('a')))

    return values


@institutions.over('public_notes', '^680..')
@utils.for_each_value
def public_notes(self, key, value):
    """Hidden note."""
    return value.get('i')


@institutions.over('historical_data', '^6781.')
def historical_data(self, key, value):
    """Historical data."""
    values = self.get('historical_data', [])
    values.extend(el for el in value.get('a'))

    return values


@institutions.over('related_institutes', '^510..')
@utils.for_each_value
def related_institutes(self, key, value):
    """Related institutes."""
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
        'record': get_record_ref(value.get('0'), record_type='institutions'),
    }
