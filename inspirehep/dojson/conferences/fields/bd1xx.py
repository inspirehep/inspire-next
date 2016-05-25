# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

from inspirehep.dojson.utils import (
    parse_conference_address,
    remove_duplicates_from_list_of_dicts)

import six

from dojson import utils

from ..model import conferences


@conferences.over('acronym', '^111')
@utils.for_each_value
def acronym(self, key, value):
    """Conference acronym."""
    def append_to_self(title):
        """Make a dictionary and append to self."""
        titles = {}
        titles['title'] = title
        titles['subtitle'] = value.get('b')
        titles['source'] = value.get('9')
        if titles:
            self['titles'].append(titles)

    self['date'] = value.get('d')
    self['opening_date'] = value.get('x')
    self['closing_date'] = value.get('y')
    self['cnum'] = value.get('g')
    self.setdefault('titles', [])
    title = value.get('a')
    if isinstance(title, (tuple, list)):
        for t in title:
            append_to_self(t)
    else:
        append_to_self(title)

    if value.get('c'):
        self.setdefault('address', [])
        raw_addresses = utils.force_list(value.get('c'))
        for raw_address in raw_addresses:
            address = parse_conference_address(raw_address)
            self['address'].append(address)

    return utils.force_list(value.get('e'))


@conferences.over('alternative_titles', '^711')
@utils.for_each_value
def alternative_titles(self, key, value):
    """Alternative title.

    711__b is for indexing and will not be displayed.
    """
    titles = {}
    titles['title'] = value.get('a')
    titles['searchable_title'] = value.get('b')
    return titles


@conferences.over('contact_details', '^270')
@utils.for_each_value
@utils.filter_values
def contact_details(self, key, value):
    """Map 270 field to contact details and extra_place_info"""
    self.setdefault('extra_place_info', [])
    extra_place_info = value.get('b')
    if isinstance(extra_place_info, six.string_types):
        self['extra_place_info'].append(extra_place_info)
    elif isinstance(extra_place_info, tuple):
        for place in extra_place_info:
            self['extra_place_info'].append(place)
    else:
        pass

    name = value.get('p')
    email = value.get('m')
    return {
        'name': name if isinstance(name, six.string_types) else None,
        'email': email if isinstance(email, six.string_types) else None
    }


@conferences.over('keywords', '^6531')
def keywords(self, key, value):
    """Field code."""
    def get_value(value):
        return {
            'value': value.get('a'),
            'source': value.get('9')
        }
    value = utils.force_list(value)
    keywords = self.get('keywords', [])
    for val in value:
        keywords.append(get_value(val))
    return remove_duplicates_from_list_of_dicts(keywords)


@conferences.over('nonpublic_note', '^595')
@utils.for_each_value
def nonpublic_note(self, key, value):
    """Non public note."""
    return value.get('a')


@conferences.over('note', '^500')
@utils.for_each_value
def note(self, key, value):
    """Public note."""
    return value.get('a')


@conferences.over('series', '^411')
@utils.for_each_value
def series(self, key, value):
    """Conference series."""
    if value.get('n'):
        series_number = ''
        try:
            series_number = int(value.get('n'))
            self['series_number'] = series_number
        except:
            pass
    return value.get('a')


@conferences.over('short_description', '^520')
@utils.for_each_value
@utils.filter_values
def short_description(self, key, value):
    """Conference short_description."""
    return {
        'value': value.get('a'),
        'source': value.get('9')
    }
