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


@hep.over('public_notes', '^500..')
@utils.for_each_value
@utils.filter_values
def public_notes(self, key, value):
    """General Note."""
    return {
        'value': value.get('a'),
        'source': value.get('9'),
    }


@hep2marc.over('500', 'public_notes')
@utils.for_each_value
@utils.filter_values
def public_notes2marc(self, key, value):
    """General Note."""
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('hidden_notes', '^595..')
def hidden_notes(self, key, value):
    """Hidden notes."""
    def get_value(value):
        return {
            'value': value.get('a'),
            'cern_reference': value.get('b'),
            'cds': value.get('c'),
            'source': value.get('9'),
        }

    hidden_note_list = self.get('hidden_notes', [])

    if isinstance(value, list):
        for element in value:
            hidden_note_list.append(get_value(element))
    else:
        hidden_note_list.append(get_value(value))
    hidden_note = []
    for element in hidden_note_list:
        if element not in hidden_note:
            hidden_note.append(element)
    return hidden_note


@hep2marc.over('595', 'hidden_notes')
@utils.for_each_value
@utils.filter_values
def hidden_note2marc(self, key, value):
    """Hidden note."""
    return {
        'a': value.get('value'),
        'b': value.get('cern_reference'),
        'c': value.get('cds'),
        '9': value.get('source'),
    }


@hep.over('thesis', '^502..')
@utils.for_each_value
@utils.filter_values
def thesis(self, key, value):
    """Get Thesis Information."""
    return {
        'defense_date': value.get('a'),
        'degree_type': value.get('b'),
        'university': value.get('c'),
        'date': value.get('d')
    }


@hep2marc.over('502', 'thesis')
@utils.for_each_value
@utils.filter_values
def thesis2marc(self, key, value):
    """Get Thesis Information."""
    return {
        'a': value.get('defense_date'),
        'b': value.get('degree_type'),
        'c': value.get('university'),
        'd': value.get('date'),
    }


@hep.over('abstracts', '^520[10_2483].')
@utils.for_each_value
@utils.filter_values
def abstracts(self, key, value):
    """Summary, Etc.."""
    return {
        'value': value.get('a'),
        'source': value.get('9'),
    }


@hep2marc.over('520', 'abstracts')
@utils.for_each_value
@utils.filter_values
def abstract2marc(self, key, value):
    """Summary, Etc.."""
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('funding_info', '^536..')
@utils.for_each_value
@utils.filter_values
def funding_info(self, key, value):
    """Funding Information Note."""
    return {
        'agency': value.get('a'),
        'grant_number': value.get('c'),
        'project_number': value.get('f'),
    }


@hep2marc.over('536', 'funding_info')
@utils.for_each_value
@utils.filter_values
def funding_info2marc(self, key, value):
    """Funding Information Note."""
    return {
        'a': value.get('agency'),
        'c': value.get('grant_number'),
        'f': value.get('project_number'),
    }


@hep.over('license', '^540..')
@utils.for_each_value
@utils.filter_values
def license(self, key, value):
    """Add Terms Governing Use and Reproduction Note."""
    return {
        'license': value.get('a'),
        'imposing': value.get('b'),
        'url': value.get('u'),
        'material': value.get('3')
    }


@hep2marc.over('540', 'license')
@utils.for_each_value
@utils.filter_values
def license2marc(self, key, value):
    """Add Terms Governing Use and Reproduction Note."""
    return {
        'a': value.get('license'),
        'b': value.get('imposing'),
        'u': value.get('url'),
        '3': value.get('material'),
    }


@hep.over('acquisition_source', '^541[10_].')
@utils.for_each_value
@utils.filter_values
def acquisition_source(self, key, value):
    """Immediate Source of Acquisition Note."""
    return {
        'source': value.get('a'),
        'email': value.get('b'),
        'method': value.get('c'),
        'date': value.get('d'),
        'submission_number': value.get('e')
    }


@hep2marc.over('541', 'acquisition_source')
@utils.for_each_value
@utils.filter_values
def acquisition_source2marc(self, key, value):
    """Immediate Source of Acquisition Note."""
    return {
        'a': value.get('source'),
        'b': value.get('email'),
        'c': value.get('method'),
        'd': value.get('date'),
        'e': value.get('submission_number'),
    }


@hep.over('copyright', '^542[10_].')
@utils.for_each_value
@utils.filter_values
def copyright(self, key, value):
    """Information Relating to Copyright Status."""
    return {
        'material': value.get('3'),
        'holder': value.get('d'),
        'statement': value.get('f'),
        'url': value.get('u'),
    }


@hep2marc.over('542', 'copyright')
@utils.for_each_value
@utils.filter_values
def copyright2marc(self, key, value):
    """Information Relating to Copyright Status."""
    return {
        '3': value.get('material'),
        'd': value.get('holder'),
        'f': value.get('statement'),
        'u': value.get('url'),
    }
