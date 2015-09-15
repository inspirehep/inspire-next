# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

from ..model import conferences


@conferences.over('acronym', '^111')
def acronym(self, key, value):
    """Conference acronym."""
    self['opening_date'] = value.get('x')
    self['closing_date'] = value.get('y')
    self['cnum'] = value.get('g')
    self['place'] = value.get('c')
    self['subtitle'] = value.get('b')
    self['title'] = value.get('a')
    return value.get('e')


@conferences.over('alternative_titles', '^711')
@utils.for_each_value
def alternative_titles(self, key, value):
    """Alternative title."""
    return value.get('a')


@conferences.over('contact_person', '^270')
@utils.for_each_value
def contact_person(self, key, value):
    """Contact person."""
    if value.get('m'):
        self['contact_email'] = value.get('m')
    return value.get('p')


@conferences.over('field_code', '^65017')
@utils.for_each_value
@utils.filter_values
def field_code(self, key, value):
    """Field code."""
    return {
        'value': value.get('a'),
        'source': value.get('9')
    }


@conferences.over('keywords', '^6531')
@utils.for_each_value
@utils.filter_values
def keywords(self, key, value):
    """Field code."""
    return {
        'value': value.get('a'),
        'source': value.get('9')
    }


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
        self['series_number'] = value.get('n')
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


@conferences.over('transparencies', '^8564')
@utils.for_each_value
def transparencies(self, key, value):
    """Conference transparencies."""
    if value.get('y', '').lower() == 'transparencies':
        return value.get('u')
