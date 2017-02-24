# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016, 2017 CERN.
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

"""DoJSON rules for Conferences."""

from __future__ import absolute_import, division, print_function

import six

from dojson import utils

from inspirehep.utils.helpers import force_force_list

from .model import conferences
from ..utils import force_single_element
from ..utils.geo import parse_conference_address


@conferences.over('acronym', '^111')
@utils.for_each_value
def acronym(self, key, value):
    self['opening_date'] = value.get('x')
    self['closing_date'] = value.get('y')

    self['cnum'] = value.get('g')

    if value.get('a'):
        self.setdefault('titles', [])
        raw_titles = force_force_list(value.get('a'))
        for raw_title in raw_titles:
            title = {
                'title': raw_title,
                'subtitle': value.get('b'),
                'source': value.get('9'),
            }
            self['titles'].append(title)

    if value.get('c'):
        self.setdefault('address', [])
        raw_addresses = force_force_list(value.get('c'))
        for raw_address in raw_addresses:
            address = parse_conference_address(raw_address)
            self['address'].append(address)

    return value.get('e')


@conferences.over('contact_details', '^270')
@utils.for_each_value
def contact_details(self, key, value):
    extra_place_info = value.get('b')
    if extra_place_info:
        address = parse_conference_address(extra_place_info)
        self.setdefault('address', []).append(address)

    name = value.get('p')
    email = value.get('m')

    return {
        'name': name if isinstance(name, six.string_types) else None,
        'email': email if isinstance(email, six.string_types) else None,
    }


@conferences.over('short_description', '^520')
@utils.for_each_value
def short_description(self, key, value):
    return {
        'value': value.get('a'),
        'source': value.get('9')
    }


@conferences.over('keywords', '^6531')
def keywords(self, key, value):
    def get_value(value):
        return {
            'value': value.get('a'),
            'source': value.get('9')
        }
    value = force_force_list(value)
    keywords = self.get('keywords', [])
    for val in value:
        keywords.append(get_value(val))
    return keywords


@conferences.over('series', '^411')
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


@conferences.over('alternative_titles', '^711')
@utils.flatten
@utils.for_each_value
def alternative_titles(self, key, value):
    return [
        {'title': value.get('a')},
        {'title': value.get('b')},
    ]
