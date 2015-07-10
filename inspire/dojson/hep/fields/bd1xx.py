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


@hep.over('authors', '^[17]00[103_].')
# @utils.filter_values
def authors(self, key, value):
    """Main Entry-Personal Name."""
    value = utils.force_list(value)

    def get_value(value):
            return {
                'full_name': value.get('a'),
                'relator_term': value.get('e'),
                'alternative_name': value.get('q'),
                'INSPIRE_id': value.get('i'),
                'external_id': value.get('j'),
                'e_mail': value.get('m'),
                'affiliation': utils.force_list(
                    value.get('u')
                ),
            }

    authors = self.get('authors', [])

    if key.startswith('100'):
        authors.insert(0, get_value(value[0]))
    else:
        for single_value in value:
            authors.append(get_value(single_value))

    return authors


@hep.over('corporate_author', '^110[10_2].')
@utils.filter_values
def corporate_author(self, key, value):
    """Main Entry-Corporate Name."""
    return {
        'corporate_author': value.get('a'),
    }


@hep.over('institution', '^110..')
@utils.filter_values
def institution(self, key, value):
    """Institution info."""
    return {
        'name': value.get('a'),
        'department': value.get('b'),
        'new_name': value.get('t'),
        'affiliation': value.get('u'),
        'obsolete_icn': value.get('x'),
    }
