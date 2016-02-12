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

from inspirehep.dojson import utils as inspire_dojson_utils
from inspirehep.dojson.utils import strip_empty_values

from ..model import hep, hep2marc


@hep.over('references', '^999C5')
def references(self, key, value):
    """Produce list of references."""
    value = utils.force_list(value)

    def get_value(value):
        recid = ''
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
        return {
            'recid': recid,
            'texkey': value.get('1'),
            'doi': value.get('a'),
            'collaboration': utils.force_list(value.get('c')),
            'editors': value.get('e'),
            'authors': utils.force_list(value.get('h')),
            'misc': utils.force_list(value.get('m')),
            'number': number,
            'isbn': value.get('i'),
            'publisher': utils.force_list(value.get('p')),
            'maintitle': value.get('q'),
            'report_number': utils.force_list(value.get('r')),
            'title': utils.force_list(value.get('t')),
            'url': utils.force_list(value.get('u')),
            'journal_pubnote': utils.force_list(value.get('s')),
            'raw_reference': utils.force_list(value.get('x')),
            'year': year,
        }
    references = self.get('references', [])

    for val in value:
        references.append(get_value(val))

    return inspire_dojson_utils.remove_duplicates_from_list(
        strip_empty_values(references))


@hep2marc.over('999C5', 'references')
@utils.for_each_value
@utils.filter_values
def references2marc(self, key, value):
    """Produce list of references."""
    return {
        '0': value.get('recid'),
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
        'u': value.get('url'),
        's': value.get('journal_pubnote'),
        'x': value.get('raw_reference'),
        'y': value.get('year'),
    }


@hep.over('refextract', '^999C6')
@utils.for_each_value
@utils.filter_values
def refextract(self, key, value):
    """Contains info from refextract."""
    return {
        'comment': value.get('c'),
        'time': value.get('t'),
        'version': utils.force_list(value.get('v')),
        'source': value.get('s'),
    }


@hep2marc.over('999C6', 'refextract')
@utils.for_each_value
@utils.filter_values
def refextract2marc(self, key, value):
    """Contains info from refextract."""
    return {
        'c': value.get('comment'),
        't': value.get('time'),
        'v': value.get('version'),
        's': value.get('source'),
    }
