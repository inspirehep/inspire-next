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

import logging

from dojson import utils

from ..model import hep, hep2marc
from ...utils import force_single_element, get_record_ref

from inspirehep.utils.helpers import force_force_list


logger = logging.getLogger(__name__)


@hep.over('public_notes', '^500..')
def public_notes(self, key, value):
    """General Note."""
    public_notes = self.get('public_notes', [])

    source = force_single_element(value.get('9'))
    notes = force_force_list(value.get('a'))

    for note in notes:
        public_notes.append({
            'source': source,
            'value': note,
        })

    return public_notes


@hep2marc.over('500', 'public_notes')
@utils.for_each_value
def public_notes2marc(self, key, value):
    """General Note."""
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('_private_notes', '^595..')
def private_notes(self, key, value):
    """Private notes."""
    def _private_notes(value):
        def _private_note(value, a=None):
            source = value.get('9')
            if value.get('c'):
                source = "CDS"
            return {
                'value': a if a else value.get('b'),
                'source': source,
            }

        if value.get('a'):
            return [_private_note(value, a) for a in force_force_list(value['a'])]
        else:
            return [_private_note(value)]

    private_notes = self.get('_private_notes', [])
    private_notes.extend(_private_notes(value))

    return private_notes


@hep2marc.over('595', '_private_notes')
@utils.for_each_value
def private_notes2marc(self, key, value):
    """Hidden note."""
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('thesis_info', '^502..')
def thesis(self, key, value):
    """Get Thesis Information."""
    DEGREE_TYPES_MAP = {
        'RAPPORT DE STAGE': 'other',
        'INTERNSHIP REPORT': 'other',
        'DIPLOMA': 'diploma',
        'BACHELOR': 'bachelor',
        'LAUREA': 'laurea',
        'MASTER': 'master',
        'THESIS': 'other',
        'PHD': 'phd',
        'PDF': 'phd',
        'PH.D. THESIS': 'phd',
        'HABILITATION': 'habilitation',
    }

    _degree_type = force_single_element(value.get('b'))
    if _degree_type:
        degree_type = DEGREE_TYPES_MAP.get(_degree_type.upper(), 'other')
    else:
        degree_type = None

    res = {
        'defense_date': value.get('a'),
        'degree_type': degree_type,
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


@hep2marc.over('502', '^thesis_info$')
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
def abstracts(self, key, value):
    """Summary, Etc.."""
    if isinstance(value.get('a'), (list, tuple)):
        logger.warning(
            'Record with double abstract. '
            'Taking first abstract: %s', value.get('a')
        )
        abstract = value.get('a')[0]
    else:
        abstract = value.get('a')

    return {
        'value': abstract,
        'source': value.get('9'),
    }


@hep2marc.over('520', 'abstracts')
@utils.for_each_value
def abstract2marc(self, key, value):
    """Summary, Etc.."""
    return {
        'a': value.get('value'),
        '9': value.get('source'),
    }


@hep.over('funding_info', '^536..')
@utils.for_each_value
def funding_info(self, key, value):
    """Funding Information Note."""
    return {
        'agency': value.get('a'),
        'grant_number': value.get('c'),
        'project_number': value.get('f'),
    }


@hep2marc.over('536', 'funding_info')
@utils.for_each_value
def funding_info2marc(self, key, value):
    """Funding Information Note."""
    return {
        'a': value.get('agency'),
        'c': value.get('grant_number'),
        'f': value.get('project_number'),
    }


@hep.over('license', '^540..')
@utils.for_each_value
def license(self, key, value):
    """Add Terms Governing Use and Reproduction Note."""
    license_value = force_force_list(value.get('a'))
    # We strip away redundant 'Open Access' string
    license_value = [val for val in license_value if license_value != 'Open Access']
    license_value = force_single_element(license_value)
    return {
        'license': license_value,
        'imposing': value.get('b'),
        'url': value.get('u'),
        'material': value.get('3')
    }


@hep2marc.over('540', '^license$')
@utils.for_each_value
def license2marc(self, key, value):
    """Add Terms Governing Use and Reproduction Note."""
    return {
        'a': value.get('license'),
        'b': value.get('imposing'),
        'u': value.get('url'),
        '3': value.get('material'),
    }


@hep.over('copyright', '^542[10_].')
@utils.for_each_value
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
def copyright2marc(self, key, value):
    """Information Relating to Copyright Status."""
    return {
        '3': value.get('material'),
        'd': value.get('holder'),
        'f': value.get('statement'),
        'u': value.get('url'),
    }
