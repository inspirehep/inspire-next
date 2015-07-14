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


@hep.over('references', '^999C5')
@utils.for_each_value
@utils.filter_values
def references(self, key, value):
    """Produce list of references."""
    return {
        'recid': value.get('0'),
        'texkey': value.get('1'),
        'doi': value.get('a'),
        'collaboration': value.get('c'),
        'editors': value.get('e'),
        'authors': value.get('h'),
        'misc': value.get('m'),
        'number': value.get('o'),
        'isbn': value.get('i'),
        'publisher': value.get('p'),
        'maintitle': value.get('q'),
        'report_number': value.get('r'),
        'title': value.get('t'),
        'url': value.get('u'),
        'journal_pubnote': value.get('s'),
        'raw_reference': value.get('x'),
        'year': value.get('y'),
    }


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
        'version': value.get('v'),
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
