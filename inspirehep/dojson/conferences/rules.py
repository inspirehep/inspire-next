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

"""DoJSON rules for Conferences."""

from __future__ import absolute_import, division, print_function

from dojson import utils

from inspirehep.utils.helpers import force_list

from .model import conferences
from ..utils import force_single_element
from ..utils.geo import parse_conference_address


@conferences.over('acronyms', '^111..')
@utils.flatten
@utils.for_each_value
def acronyms(self, key, value):
    self['opening_date'] = value.get('x')
    self['closing_date'] = value.get('y')

    self['cnum'] = value.get('g')

    if value.get('a'):
        self.setdefault('titles', [])
        raw_titles = force_list(value.get('a'))
        for raw_title in raw_titles:
            title = {
                'title': raw_title,
                'subtitle': value.get('b'),
                'source': value.get('9'),
            }
            self['titles'].append(title)

    if value.get('c'):
        self.setdefault('address', [])
        raw_addresses = force_list(value.get('c'))
        for raw_address in raw_addresses:
            address = parse_conference_address(raw_address)
            self['address'].append(address)

    return force_list(value.get('e'))


@conferences.over('contact_details', '^270..')
def contact_details(self, key, value):
    if value.get('b'):
        self.setdefault('address', [])
        self['address'].append({'place_name': value.get('b')})

    result = []

    m_values = force_list(value.get('m'))
    p_values = force_list(value.get('p'))

    # XXX: we zip only when they have the same length, otherwise
    #      we might match an email with the wrong name.
    if len(m_values) == len(p_values):
        for m_value, p_value in zip(m_values, p_values):
            result.append({
                'email': m_value,
                'name': p_value,
            })
    else:
        for m_value in m_values:
            result.append({'email': m_value})

    return result


@conferences.over('series', '^411..')
def series(self, key, value):
    def _get_name(value):
        return force_single_element(value.get('a'))

    def _get_number(value):
        n_value = force_single_element(value.get('n'))
        if n_value and n_value.isdigit():
            return int(n_value)

    def _last_is_incomplete(series, key):
        return series and not series[-1].get(key)

    series = self.get('series', [])

    name = _get_name(value)
    number = _get_number(value)

    if name and number is None and _last_is_incomplete(series, 'name'):
        series[-1]['name'] = name
    elif number and name is None and _last_is_incomplete(series, 'number'):
        series[-1]['number'] = number
    else:
        series.append({
            'name': name,
            'number': number,
        })

    return series


@conferences.over('short_description', '^520..')
def short_description(self, key, value):
    result = self.get('short_description', {})

    if result and value.get('a'):
        result['value'] += '\n' + value.get('a')
    elif value.get('a'):
        result['value'] = value.get('a')

    return result


@conferences.over('alternative_titles', '^711..')
@utils.flatten
@utils.for_each_value
def alternative_titles(self, key, value):
    result = []

    for a_value in force_list(value.get('a')):
        result.append({'title': a_value})

    for b_value in force_list(value.get('b')):
        result.append({'title': b_value})

    return result
