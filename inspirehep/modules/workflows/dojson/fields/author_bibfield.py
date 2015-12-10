# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""
Legacy workflow author metadata in BibField conversion to updated data model.
"""

from __future__ import absolute_import, print_function, unicode_literals

import copy

from ..model import author_bibfield


@author_bibfield.over('status', '^status$')
def status(self, key, value):
    return value


@author_bibfield.over('phd_advisors', '^phd_advisors$')
def phd_advisors(self, key, value):
    return value


@author_bibfield.over('name', '^name$')
def name(self, key, value):
    out = copy.deepcopy(value)
    if value.get('last'):
        out['value'] = value['last'] + ', ' + value['first']
        del out['last']
    else:
        out['value'] = value.get('first', '')
    if value.get('first'):
        del out['first']
    return out


@author_bibfield.over('native_name', '^native_name$')
def native_name(self, key, value):
    return value


@author_bibfield.over('experiments', '^experiments$')
def experiments(self, key, value):
    return value


@author_bibfield.over('positions', '^positions$')
def positions(self, key, value):
    positions = []
    for position in value:
        positions.append({
            'institution': {'name': position['institution']},
            'rank': position['rank'],
            'start_date': position['start_date'],
            'end_date': position['end_date'],
            'email': position.get('email', ''),
            'old_email': position.get('old_email', ''),
            'status': position['status'],
        })

    return positions


@author_bibfield.over('acquisition_source', '^acquisition_source$')
def acquisition_source(self, key, value):
    out = copy.deepcopy(value)
    out['source'] = \
        value['source'][0]

    return out


@author_bibfield.over('ids', '^ids$')
def ids(self, key, value):
    return value


@author_bibfield.over('field_categories', '^field_categories$')
def field_categories(self, key, value):
    categories = []
    for category in value:
        categories.append(category['name'])
    return categories


@author_bibfield.over('urls', '^urls$')
def urls(self, key, value):
    return value


@author_bibfield.over('collections', '^collections$')
def collections(self, key, value):
    return [value]
