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

from inspire.dojson import utils as inspire_dojson_utils

from ..model import hep, hep2marc


@hep.over('authors', '^[17]00[103_].')
def authors(self, key, value):
    """Main Entry-Personal Name."""
    value = utils.force_list(value)

    def get_value(value):
        affiliations = []
        if value.get('u'):
            affiliations = list(set(utils.force_list(
                value.get('u'))))
            affiliations = [{'value': aff} for aff in affiliations]
        return {
            'full_name': value.get('a'),
            'role': value.get('e'),
            'alternative_name': value.get('q'),
            'inspire_id': value.get('i'),
            'orcid': value.get('j'),
            'recid': value.get('x'),
            'email': value.get('m'),
            'affiliations': affiliations,
            'profile': inspire_dojson_utils.create_profile_url(
                value.get('x')
            ),
            'claimed': value.get('y')
        }

    authors = self.get('authors', [])

    if key.startswith('100'):
        authors.insert(0, get_value(value[0]))
    else:
        for single_value in value:
            authors.append(get_value(single_value))
    filtered_authors = []
    for element in authors:
        if element not in filtered_authors:
            filtered_authors.append(element)
    return filtered_authors


@hep2marc.over('100', '^authors$')
def authors2marc(self, key, value):
    """Main Entry-Personal Name."""
    value = utils.force_list(value)

    def get_value(value):
        affiliations = [
            aff.get('value') for aff in value.get('affiliations', [])
        ]
        return {
            'a': value.get('full_name'),
            'e': value.get('role'),
            'q': value.get('alternative_name'),
            'i': value.get('inspire_id'),
            'j': value.get('orcid'),
            'm': value.get('email'),
            'u': affiliations,
            'x': value.get('recid'),
            'y': value.get('claimed')
        }

    if len(value) > 1:
        self["700"] = []
    for author in value[1:]:
        self["700"].append(get_value(author))
    return get_value(value[0])


@hep.over('corporate_author', '^110[10_2].')
@utils.for_each_value
def corporate_author(self, key, value):
    """Main Entry-Corporate Name."""
    return value.get('a')


@hep2marc.over('110', '^corporate_author$')
@utils.for_each_value
def corporate_author2marc(self, key, value):
    """Main Entry-Corporate Name."""
    return {
        'a': value,
    }
