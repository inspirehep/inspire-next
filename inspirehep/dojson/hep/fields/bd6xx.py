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

from ..model import hep, hep2marc


@hep.over('subject_terms', '^650[1_][_7]')
@utils.for_each_value
@utils.filter_values
def subject_terms(self, key, value):
    """Subject Added Entry-Topical Term."""
    return {
        'term': value.get('a'),
        'scheme': value.get('2'),
        'source': value.get('9'),
    }


@hep2marc.over('65017', 'subject_terms')
@utils.for_each_value
@utils.filter_values
def subject_terms2marc(self, key, value):
    """Subject Added Entry-Topical Term."""
    return {
        'a': value.get('term'),
        '2': value.get('scheme'),
        '9': value.get('source'),
    }


@hep.over('free_keywords', '^653[10_2][_1032546]')
@utils.for_each_value
@utils.filter_values
def free_keywords(self, key, value):
    """Free keywords."""
    return {
        'value': value.get('a'),
        'source': value.get('9'),
    }


@hep2marc.over('653', 'free_keywords')
@utils.for_each_value
@utils.filter_values
def free_keywords2marc(self, key, value):
    """Free keywords."""
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('accelerator_experiments', '^693..')
@utils.for_each_value
@utils.filter_values
def accelerator_experiments(self, key, value):
    """The accelerator/experiment related to this record."""
    recid = ''
    curated_relation = False
    if '0' in value:
        try:
            recid = int(value.get('0'))
        except (TypeError, ValueError, AttributeError):
            pass
    if recid:
        curated_relation = True
    return {
        'recid': recid,
        'accelerator': value.get('a'),
        'experiment': value.get('e'),
        'curated_relation': curated_relation
    }


@hep2marc.over('693', 'accelerator_experiments')
@utils.for_each_value
@utils.filter_values
def accelerator_experiments2marc(self, key, value):
    """The accelerator/experiment related to this record."""
    return {
        'a': value.get('accelerator'),
        'e': value.get('experiment'),
    }


@hep.over('thesaurus_terms', '^695..')
def thesaurus_terms(self, key, value):
    """Controlled keywords."""
    def get_value(value):
        try:
            energy_range = int(value.get('e'))
        except (TypeError, ValueError):
            energy_range = None
        return {
            'keyword': value.get('a'),
            'energy_range': energy_range,
            'classification_scheme': value.get('2'),
        }
    thesaurus_terms_list = self.get('thesaurus_terms', [])

    if isinstance(value, list):
        for element in value:
            thesaurus_terms_list.append(get_value(element))
    else:
        thesaurus_terms_list.append(get_value(value))
    thesaurus_terms = [dict(t) for t in set([tuple(d.items()) for d
                       in thesaurus_terms_list])]
    return thesaurus_terms


@hep2marc.over('695', 'thesaurus_terms')
@utils.for_each_value
@utils.filter_values
def thesaurus_terms2marc(self, key, value):
    """Controlled keywords."""
    return {
        'a': value.get('keyword'),
        'e': value.get('energy_range'),
        '2': value.get('classification_scheme'),
    }
