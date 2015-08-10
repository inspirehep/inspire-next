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


@hep.over('publication_info', '^773..')
@utils.for_each_value
@utils.filter_values
def publication_info(self, key, value):
    """Publication info about record."""
    return {
        'recid': value.get('0'),
        'page_artid': value.get('c'),
        'journal_issue': value.get('n'),
        'conf_acronym': value.get('o'),
        'journal_title': value.get('p'),
        'reportnumber': value.get('r'),
        'confpaper_info': value.get('t'),
        'journal_volume': value.get('v'),
        'cnum': value.get('w'),
        'pubinfo_freetext': value.get('x'),
        'year': value.get('y'),
        'isbn': value.get('z'),
    }


@hep2marc.over('773', 'publication_info')
@utils.for_each_value
@utils.filter_values
def publication_info2marc(self, key, value):
    """Publication info about record."""
    return {
        '0': value.get('recid'),
        'c': value.get('page_artid'),
        'n': value.get('journal_issue'),
        'o': value.get('conf_acronym'),
        'p': value.get('journal_title'),
        'r': value.get('reportnumber'),
        't': value.get('confpaper_info'),
        'v': value.get('journal_volume'),
        'w': value.get('cnum'),
        'x': value.get('pubinfo_freetext'),
        'y': value.get('year'),
        'z': value.get('isbn'),
    }


@hep.over('succeeding_entry', '^785..')
@utils.for_each_value
@utils.filter_values
def succeeding_entry(self, key, value):
    """Succeeding Entry."""
    return {
        'relationship_code': value.get('r'),
        'recid': value.get('w'),
        'isbn': value.get('z'),
    }


@hep2marc.over('785', 'succeeding_entry')
@utils.for_each_value
@utils.filter_values
def succeeding_entry2marc(self, key, value):
    """Succeeding Entry."""
    return {
        'r': value.get('relationship_code'),
        'w': value.get('recid'),
        'z': value.get('isbn'),
    }
