# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON rules for MARC fields in 7xx."""

from __future__ import absolute_import, division, print_function

from dojson import utils

from inspire_schemas.utils import load_schema
from inspirehep.utils.helpers import force_list, maybe_int
from inspirehep.utils.pubnote import split_page_artid

from ..model import hep, hep2marc
from ...utils import (
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
)


@hep.over('collaborations', '^710..')
@utils.for_each_value
def collaborations(self, key, value):
    return {
        'record': get_record_ref(maybe_int(value.get('0')), 'experiments'),
        'value': value.get('g'),
    }


@hep2marc.over('710', '^collaborations$')
@utils.for_each_value
def collaborations2marc(self, key, value):
    return {'g': value.get('value')}


@hep.over('publication_info', '^773..')
@utils.for_each_value
def publication_info(self, key, value):
    def _get_material(value):
        schema = load_schema('elements/material')
        valid_materials = schema['enum']

        m_value = force_single_element(value.get('m', ''))
        for material in valid_materials:
            if m_value.lower() == material:
                return material

    year = maybe_int(force_single_element(value.get('y')))
    parent_recid = maybe_int(force_single_element(value.get('0')))
    journal_recid = maybe_int(force_single_element(value.get('1')))
    conference_recid = maybe_int(force_single_element(value.get('2')))
    parent_record = get_record_ref(parent_recid, 'literature')
    conference_record = get_record_ref(conference_recid, 'conferences')
    journal_record = get_record_ref(journal_recid, 'journals')

    page_start, page_end, artid = split_page_artid(value.get('c'))

    res = {
        'parent_record': parent_record,
        'conference_record': conference_record,
        'journal_record': journal_record,
        'page_start': page_start,
        'page_end': page_end,
        'artid': artid,
        'journal_issue': force_single_element(value.get('n')),
        'conf_acronym': force_single_element(value.get('o')),
        'journal_title': force_single_element(value.get('p')),
        'parent_report_number': force_single_element(value.get('r')),
        'journal_volume': force_single_element(value.get('v')),
        'cnum': force_single_element(value.get('w')),
        'pubinfo_freetext': force_single_element(value.get('x')),
        'year': year,
        'parent_isbn': force_single_element(value.get('z')),
        'material': _get_material(value),
        'hidden': key.startswith('7731') or None,
    }

    return res


@hep2marc.over('773', '^publication_info$')
def publication_info2marc(self, key, values):
    """Populate the ``773`` MARC field.

    Also populates the ``7731`` MARC field through side effects.
    """
    result_773 = self.get('773', [])
    result_7731 = self.get('7731', [])

    for value in force_list(values):
        page_artid = []
        if value.get('page_start') and value.get('page_end'):
            page_artid.append('{page_start}-{page_end}'.format(**value))
        elif value.get('page_start'):
            page_artid.append('{page_start}'.format(**value))
        if value.get('artid'):
            page_artid.append(u'{artid}'.format(**value))

        result = {
            '0': get_recid_from_ref(value.get('parent_record')),
            'c': page_artid,
            'm': value.get('material'),
            'n': value.get('journal_issue'),
            'o': value.get('conf_acronym'),
            'p': value.get('journal_title'),
            'r': value.get('parent_report_number'),
            'v': value.get('journal_volume'),
            'w': value.get('cnum'),
            'x': value.get('pubinfo_freetext'),
            'y': value.get('year'),
            'z': value.get('parent_isbn'),
        }

        if value.get('hidden'):
            result_7731.append(result)
        else:
            result_773.append(result)

    self['7731'] = result_7731
    return result_773


@hep.over('succeeding_entry', '^785..')
def succeeding_entry(self, key, value):
    if isinstance(value, (tuple, list)):
        # Too bad: there can only be one succeeding entry.
        value = value[0]

    return {
        'relationship_code': value.get('r'),
        'record': get_record_ref(value.get('w'), 'literature'),
        'isbn': value.get('z'),
    }


@hep2marc.over('785', '^succeeding_entry$')
def succeeding_entry2marc(self, key, value):
    return {
        'r': value.get('relationship_code'),
        'w': get_recid_from_ref(value.get('record')),
        'z': value.get('isbn'),
    }
