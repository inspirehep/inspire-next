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

from isbn import ISBNError

from dojson import utils
from idutils import normalize_isbn

from ..model import hep, hep2marc


@hep.over('isbns', '^020..')
@utils.for_each_value
@utils.filter_values
def isbns(self, key, value):
    "ISBN, its medium and an additional comment."""
    try:
        isbn = normalize_isbn(value['a'])
    except (KeyError, ISBNError):
        return {}

    b = value.get('b', '').lower()
    if 'online' == b:
        medium = 'online'
        comment = ''
    elif 'print' == b:
        medium = 'print'
        comment = ''
    elif 'electronic' in b:
        medium = 'online'
        comment = 'electronic'
    elif 'ebook' in b:
        medium = 'online'
        comment = 'ebook'
    elif 'hardcover' in b:
        medium = 'print'
        comment = 'hardcover'
    else:
        medium = ''
        comment = b

    return {
        'medium': medium,
        'value': isbn,
        'comment': comment,
    }


@hep2marc.over('020', 'isbns')
@utils.for_each_value
@utils.filter_values
def isbns2marc(self, key, value):
    """Other Standard Identifier."""
    return {
        'a': value.get('value'),
        'b': value.get('medium'),
    }


@hep.over('persistent_identifiers', '^024..')
def persistent_identifiers(self, key, value):
    """Persistent Standard Identifiers."""
    value = utils.force_list(value)

    dois = self.get('dois', [])
    persistent_identifiers = self.get('persistent_identifiers', [])
    for val in value:
        if val:
            items = utils.force_list(val.get('a'))
            if val.get("2") and val.get("2", '').lower() == "doi":
                for v in items:
                    dois.append({
                        'value': v,
                        'source': val.get('9')
                    })
            else:
                for v in items:
                    persistent_identifiers.append({
                        'value': v,
                        'source': val.get('9'),
                        'type': val.get('2')
                    })
    self['dois'] = dois
    return persistent_identifiers


@hep2marc.over('024', '^(dois|persistent_identifiers)$')
def dois2marc(self, key, value):
    """Other Standard Identifier."""
    value = utils.force_list(value)

    def get_value(val):
        return {
            'a': val.get('value'),
            '9': val.get('source'),
            '2': val.get('type') or "DOI"
        }

    self['024'] = self.get('024', [])
    for val in value:
        self['024'].append(get_value(val))
    return self['024']


@hep.over('external_system_numbers', '^035..')
def external_system_numbers(self, key, value):
    """System Control Number."""
    value = utils.force_list(value)

    def get_value(value):
        return {
            'value': value.get('a'),
            'institute': value.get('9'),
            'obsolete': bool(value.get('z')),
        }

    external_system_numbers = self.get('external_system_numbers', [])

    for val in value:
        external_system_numbers.append(get_value(val))
    return external_system_numbers


@hep2marc.over('035', 'external_system_numbers')
@utils.for_each_value
@utils.filter_values
def external_system_numbers2marc(self, key, value):
    """System Control Number."""
    return {
        'a': value.get('value'),
        '9': value.get('institute'),
        'z': value.get('obsolete'),
    }


@hep.over('report_numbers', '^037..')
def report_numbers(self, key, value):
    """Report numbers and arXiv numbers from 037."""
    def get_value(value):
        return {
            'source': value.get('9'),
            'value': value.get('a', value.get('z')),
        }

    def get_value_arxiv(value):
        return {
            'value': value.get('a'),
            'categories': utils.force_list(value.get('c')),
        }

    report_number = self.get('report_numbers', [])
    arxiv_eprints = self.get('arxiv_eprints', [])

    value = utils.force_list(value)
    for element in value:
        if element.get('9') and element.get('9') == 'arXiv' and 'c' in element:
            arxiv_eprints.append(get_value_arxiv(element))
        else:
            report_number.append(get_value(element))

    self['arxiv_eprints'] = arxiv_eprints
    return report_number


@hep2marc.over('037', '(arxiv_eprints|report_numbers)')
def report_numbers2marc(self, key, value):
    """Source of Acquisition."""
    value = utils.force_list(value)

    def get_value(value):
        if key == "report_numbers":
            return {
                'a': value.get('value'),
                '9': value.get('source'),
            }
        elif key == "arxiv_eprints":
            return {
                'a': value.get('value'),
                'c': value.get('categories'),
                '9': "arXiv",
            }

    self['037'] = self.get('037', [])
    for rn in value:
        self['037'].append(get_value(rn))
    return self['037']


@hep.over('languages', '^041[10_].')
def languages(self, key, value):
    """Language Code."""
    values = utils.force_list(value)
    languages = self.get('languages', [])
    for value in values:
        if value.get('a'):
            languages.append(value.get('a'))
    return languages


@hep2marc.over('041', 'languages')
@utils.for_each_value
@utils.filter_values
def languages2marc(self, key, value):
    """Language Code."""
    return {
        'a': value,
    }


@hep.over('classification_number', '^084..')
@utils.for_each_value
@utils.filter_values
def classification_number(self, key, value):
    """Other Classification Number."""
    return {
        'classification_number': value.get('a'),
        'standard': value.get('2'),
        'source': value.get('9')
    }


@hep2marc.over('084', 'classification_number')
@utils.for_each_value
@utils.filter_values
def classification_number2marc(self, key, value):
    """Other Classification Number."""
    return {
        'a': value.get('classification_number'),
        '2': value.get('standard'),
        '9': value.get('source'),
    }
