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

from dojson import utils

from ..model import hep, hep2marc
from ...utils import force_force_list, get_record_ref


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
    def _hidden_notes(value):
        def _hidden_note(value, a=None):
            return {
                'value': a,
                'cern_reference': value.get('b'),
                'cds': value.get('c'),
                'source': value.get('9'),
            }

        if value.get('a'):
            return [_hidden_note(value, a) for a in force_force_list(value['a'])]
        else:
            return [_hidden_note(value)]

    hidden_notes = self.get('hidden_notes', [])
    hidden_notes.extend(_hidden_notes(value))

    return hidden_notes


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
@utils.filter_values
def thesis(self, key, value):
    """Get Thesis Information."""
    res = {
        'defense_date': value.get('a'),
        'degree_type': value.get('b'),
        'date': value.get('d'),
    }

    inst_names = force_force_list(value.get('c', []))
    inst_recids = force_force_list(value.get('z', []))
    if len(inst_names) != len(inst_recids):
        institutions = [{'name': name} for name in inst_names]
    else:
        institutions = [{'name': name,
                         'record': get_record_ref(recid, 'institutions'),
                         'curated_relation': True}
                        for name, recid in zip(inst_names, inst_recids)]
    if institutions:
        res['institutions'] = institutions
    return res


@hep2marc.over('502', '^thesis$')
@utils.filter_values
def thesis2marc(self, key, value):
    """Get Thesis Information."""
    return {
        'a': value.get('defense_date'),
        'b': value.get('degree_type'),
        'c': [inst['name'] for inst in value.get('institutions', [])],
        'd': value.get('date'),
    }


@hep.over('abstracts', '^520[10_2483].')
@utils.for_each_value
@utils.filter_values
def abstracts(self, key, value):
    """Summary, Etc.."""
    if isinstance(value.get('a'), (list, tuple)):
        import warnings
        warnings.warn("Record with double abstract! Taking first abstract: {}".format(value.get('a')[0]))
        abstract = value.get('a')[0]
    else:
        abstract = value.get('a')
    return {
        'value': abstract,
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


@hep2marc.over('540', '^license$')
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
def acquisition_source(self, key, value):
    """Immediate Source of Acquisition Note."""
    return {
        'source': value.get('a'),
        'email': value.get('b'),
        'method': value.get('c'),
        'date': value.get('d'),
        'submission_number': str(value.get('e'))
    }


@hep2marc.over('541', 'acquisition_source')
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
