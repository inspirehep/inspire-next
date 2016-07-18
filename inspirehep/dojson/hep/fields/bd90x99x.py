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

import re

from isbn import ISBNError

from dojson import utils
from idutils import normalize_isbn

from ..model import hep, hep2marc
from ...utils import (
    get_recid_from_ref,
    get_record_ref,
    strip_empty_values,
)

from inspirehep.utils.helpers import force_force_list


RE_VALID_PUBNOTE = re.compile(".*,.*,.*(,.*)?")


@hep.over('references', '^999C5')
def references(self, key, value):
    """Produce list of references."""
    value = force_force_list(value)

    def get_valid_pubnotes(pubnotes):
        valid_pubnotes = []
        raw_references = []
        if pubnotes:
            for pubnote in pubnotes:
                if RE_VALID_PUBNOTE.match(pubnote):
                    valid_pubnotes.append(pubnote)
                else:
                    raw_references.append(pubnote)
        return valid_pubnotes, raw_references

    def get_value(value):
        recid = None
        number = ''
        year = ''
        if '0' in value:
            try:
                recid = int(value.get('0'))
            except:
                pass
        if 'o' in value:
            try:
                number = int(value.get('o'))
            except:
                pass
        if 'y' in value:
            try:
                year = int(value.get('y'))
            except:
                pass

        try:
            isbn = normalize_isbn(value['i'])
        except (KeyError, ISBNError):
            isbn = ''

        valid_pubnotes, raw_references = get_valid_pubnotes(force_force_list(value.get('s')))

        if value.get('x'):
            raw_references += list(force_force_list(value.get('x')))

        return {
            'record': get_record_ref(recid, 'literature'),
            'texkey': value.get('1'),
            'doi': value.get('a'),
            'collaboration': force_force_list(value.get('c')),
            'editors': value.get('e'),
            'authors': force_force_list(value.get('h')),
            'misc': force_force_list(value.get('m')),
            'number': number,
            'isbn': isbn,
            'publisher': force_force_list(value.get('p')),
            'maintitle': value.get('q'),
            'report_number': force_force_list(value.get('r')),
            'title': force_force_list(value.get('t')),
            'urls': force_force_list(value.get('u')),
            'journal_pubnote': valid_pubnotes,
            'raw_reference': raw_references,
            'year': year,
        }
    references = self.get('references', [])

    for val in value:
        json_val = strip_empty_values(get_value(val))
        if json_val not in references:
            references.append(json_val)

    return references


@hep2marc.over('999C5', 'references')
@utils.for_each_value
@utils.filter_values
def references2marc(self, key, value):
    """Produce list of references."""
    return {
        '0': get_recid_from_ref(value.get('record')),
        '1': value.get('texkey'),
        'a': value.get('doi'),
        'c': value.get('collaboration'),
        'e': value.get('editors'),
        'h': value.get('authors'),
        'm': value.get('misc'),
        'o': value.get('number'),
        'i': value.get('isbn'),
        'p': value.get('publisher'),
        'q': value.get('maintitle'),
        'r': value.get('report_number'),
        't': value.get('title'),
        'u': value.get('urls'),
        's': value.get('journal_pubnote'),
        'x': value.get('raw_reference'),
        'y': value.get('year'),
    }
