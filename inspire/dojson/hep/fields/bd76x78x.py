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
