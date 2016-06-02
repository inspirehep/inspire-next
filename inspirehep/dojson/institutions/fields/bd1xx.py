# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

from dojson import utils

from ..model import institutions
from ...utils.geo import parse_institution_address


@institutions.over('location', '^034..')
@utils.filter_values
def location(self, key, value):
    """GPS location info."""
    longitude, latitude = ('', '')
    if value.get('d'):
        try:
            longitude = float(value.get('d'))
        except:
            pass
    if value.get('f'):
        try:
            latitude = float(value.get('f'))
        except:
            pass
    return {
        'longitude': longitude,
        'latitude': latitude
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
        val = utils.force_list(val) or []
        if val:
            self.setdefault(key, [])
            self[key].extend(val)

    if value.get('a'):
        self.setdefault('breadcrumb_title', value.get('a'))

    set_value('institution', value.get('a'))
    set_value('department', value.get('b'))
    set_value('ICN', value.get('u'))
    set_value('obsolete_ICN', value.get('x'))
    set_value('new_ICN', value.get('t'))

    names = list(utils.force_list(value.get('a'))) or []
    names.extend(utils.force_list(value.get('u')) or [])
    names.extend(utils.force_list(value.get('t')) or [])
    return names


@institutions.over('address', '^371..')
@utils.for_each_value
@utils.filter_values
def address(self, key, value):
    """Address info."""
    return parse_institution_address(
        value.get('a'),
        value.get('b'),
        value.get('c'),
        value.get('d'),
        value.get('e'),
        utils.force_list(value.get('g')),
    )


@institutions.over('field_activity', '^372..')
@utils.for_each_value
def field_activity(self, key, value):
    """Field of activity."""
    return value.get('a')


@institutions.over('name_variants', '^410..')
@utils.for_each_value
@utils.filter_values
def name_variants(self, key, value):
    """Variants of the name."""
    if value.get('g'):
        self.setdefault('extra_words', [])
        self['extra_words'].extend(utils.force_list(value.get('g')))
    return {
        "source": value.get('9'),
        "value": utils.force_list(value.get('a'))
    }


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
@utils.for_each_value
def hidden_notes(self, key, value):
    """Hidden note."""
    return value.get('a')


@institutions.over('public_notes', '^680..')
@utils.for_each_value
def public_notes(self, key, value):
    """Hidden note."""
    return value.get('i')


@institutions.over('urls', '^856.[10_28]')
@utils.for_each_value
def urls(self, key, value):
    """Contact person."""
    return value.get('u')


@institutions.over('historical_data', '^6781..')
@utils.for_each_value
def historical_data(self, key, value):
    """Historical data."""
    return value.get('a')
