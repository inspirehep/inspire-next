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
    return value.get('e')


@conferences.over('closing_date', '^111')
def closing_date(self, key, value):
    """Conference closing_date."""
    return value.get('y')


@conferences.over('opening_date', '^111')
def opening_date(self, key, value):
    """Conference opening_date."""
    return value.get('x')


@conferences.over('cnum', '^111')
def cnum(self, key, value):
    """Conference cnum."""
    return value.get('g')


@conferences.over('place', '^111')
def place(self, key, value):
    """Conference place."""
    return value.get('c')


@conferences.over('subtitle', '^111')
def subtitle(self, key, value):
    """Conference subtitle."""
    return value.get('b')


@conferences.over('title', '^111')
def title(self, key, value):
    """Conference title."""
    return value.get('a')


@conferences.over('alternative_titles', '^711')
@utils.for_each_value
def alternative_titles(self, key, value):
    """Alternative title."""
    return value.get('a')


@conferences.over('contact_person', '^270')
@utils.for_each_value
def contact_person(self, key, value):
    """Contact person."""
    return value.get('p')


@conferences.over('contact_email', '^270')
@utils.for_each_value
def contact_email(self, key, value):
    """Contact email."""
    return value.get('m')


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
    return value.get('a')


@conferences.over('series_number', '^411')
@utils.for_each_value
def series_number(self, key, value):
    """Conference series_number."""
    return value.get('n')


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
def transparencies(self, key, value):
    """Conference transparencies."""
    if value.get('y', '').lower() == 'transparencies':
        return value.get('u')
