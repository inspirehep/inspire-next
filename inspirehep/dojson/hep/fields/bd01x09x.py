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

from dojson import utils

from inspirehep.dojson import utils as inspire_dojson_utils

from ..model import hep, hep2marc

from inspirehep.dojson.utils import strip_empty_values


@hep.over('isbns', '^020..')
@utils.for_each_value
@utils.filter_values
def isbns(self, key, value):
    """Other Standard Identifier."""
    return {
        'value': value.get('a'),
        'medium': value.get('b')
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


@hep.over('dois', '^024[1032478_][10_]')
def dois(self, key, value):
    """Other Standard Identifier."""
    value = utils.force_list(value)
    value = strip_empty_values(value)
    dois = self.get('dois', [])
    for val in value:
        if val:
            for k, v in val.iteritems():
                val[k] = utils.force_list(v)
            if val.get("2") and val.get("2", '')[0].lower() == "doi":
                for v in val.get('a'):
                    dois.append({
                        'value': v,
                        'source': val.get('9', [''])[0]
                    })
    return inspire_dojson_utils.remove_duplicates_from_list_of_dicts(dois)


@hep.over('persistent_identifiers', '^024[1032478_][10_]')
def persistent_identifiers(self, key, value):
    """Persistent identifiers."""
    value = utils.force_list(value)
    out = []
    for val in value:
        if val:
            if isinstance(val.get("2"), list):
                if val.get("2", '')[0].lower() != "doi":
                    out.append({
                        'value': utils.force_list(val.get('a')),
                        'source': val.get('9'),
                        'type': val.get('2')[0]
                    })
            else:
                if val.get("2", '').lower() != "doi":
                    out.append({
                        'value': utils.force_list(val.get('a')),
                        'source': val.get('9'),
                        'type': val.get('2')
                    })
    return out


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
    return inspire_dojson_utils.remove_duplicates_from_list_of_dicts(
        external_system_numbers)


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
    """Source of Acquisition."""
    value = utils.force_list(value)

    def get_value(value):
        return {
            'source': value.get('9'),
            'value': value.get('a', value.get('z')),
        }

    report_number = self.get('report_numbers', [])

    for element in value:
        if ('9' in element and element['9'] != 'arXiv') or '9'\
                not in element:
            report_number.append(get_value(element))
    for element in report_number:
        if isinstance(element['value'], list):
            return report_number
    return inspire_dojson_utils.remove_duplicates_from_list_of_dicts(
        report_number)


@hep2marc.over('037', 'report_numbers')
def report_numbers2marc(self, key, value):
    """Source of Acquisition."""
    value = utils.force_list(value)

    def get_value(value):
        return {
            'a': value.get('value'),
            '9': value.get('source'),
        }

    self['037'] = self.get('037', [])
    for rn in value:
        self['037'].append(get_value(rn))
    return self['037']


@hep.over('arxiv_eprints', '^037..')
def arxiv_eprints(self, key, value):
    """ArXiv identifiers to JSON."""
    value = utils.force_list(value)

    def get_value(value):
        return {
            'value': value.get('a'),
            'categories': utils.force_list(value.get('c')),
        }

    arxiv_eprints = self.get('arxiv_eprints', [])

    for element in value:
        if element['9'] == 'arXiv' and 'c' in element:
            arxiv_eprints.append(get_value(element))

    return arxiv_eprints


@hep2marc.over('037', 'arxiv_eprints')
def arxiv_eprints2marc(self, key, value):
    """Arxiv identifiers to MARC."""
    value = utils.force_list(value)

    def get_value(value):
        return {
            'a': value.get('value'),
            'c': value.get('categories'),
            '9': "arXiv"
        }

    self['037'] = self.get('037', [])
    for arxiv in value:
        self['037'].append(get_value(arxiv))
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
