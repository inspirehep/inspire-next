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

from ..model import hep


@hep.over('subject_term', '^650[1_][_7]')
@utils.for_each_value
@utils.filter_values
def subject_term(self, key, value):
    """Subject Added Entry-Topical Term."""
    return {
        'value': value.get('a'),
        'scheme': value.get('2'),
        'source': value.get('9'),
    }


@hep.over('free_keyword', '^653[10_2][_1032546]')
@utils.for_each_value
@utils.filter_values
def free_keyword(self, key, value):
    """Free keywords."""
    return {
        'value': value.get('a'),
        'source': value.get('9'),
    }


@hep.over('accelerator_experiment', '^693..')
@utils.for_each_value
@utils.filter_values
def accelerator_experiment(self, key, value):
    """The accelerator/experiment related to this record."""
    return {
        'accelerator': value.get('a'),
        'experiment': value.get('e'),
    }


@hep.over('thesaurus_terms', '^695..')
@utils.for_each_value
@utils.filter_values
def thesaurus_terms(self, key, value):
    """Controlled keywords."""
    return {
        'keyword': value.get('a'),
        'energy_range': value.get('e'),
        'classification_scheme': value.get('2'),
    }
