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

from dojson import utils

from ..model import hep, hep2marc
from ...utils import create_profile_url, get_recid_from_ref, get_record_ref


@hep.over('authors', '^[17]00[103_].')
def authors(self, key, value):
    """Main Entry-Personal Name."""
    value = utils.force_list(value)

    def get_value(value):
        affiliations = []
        if value.get('u'):
            recid = None
            try:
                recid = int(value.get('z'))
            except:
                pass
            affiliations = utils.force_list(value.get('u'))
            record = get_record_ref(recid, 'institutions')
            affiliations = [{'value': aff, 'record': record} for
                            aff in affiliations]
        person_recid = None
        if value.get('x'):
            try:
                person_recid = int(value.get('x'))
            except:
                pass
        inspire_id = ''
        if value.get('i'):
            inspire_id = utils.force_list(value.get('i'))[0]
        person_record = get_record_ref(person_recid, 'authors')
        ret = {
            'full_name': value.get('a'),
            'role': value.get('e'),
            'alternative_name': value.get('q'),
            'inspire_id': inspire_id,
            'inspire_bai': value.get('w'),
            'orcid': value.get('j'),
            'record': person_record,
            'email': value.get('m'),
            'affiliations': affiliations,
            'profile': {"__url__": create_profile_url(value.get('x'))},
            'curated_relation': value.get('y', 0) == 1
        }
        # HACK: This is to workaround broken records where multiple authors
        # got meshed up together.
        if isinstance(ret['full_name'], (list, tuple)):
            import warnings
            warnings.warn("Record with mashed-up author list! Taking first author: {}".format(value))
            ret['full_name'] = ret['full_name'][0]
        return ret

    authors = self.get('authors', [])

    if key.startswith('100'):
        authors.insert(0, get_value(value[0]))
    else:
        for single_value in value:
            authors.append(get_value(single_value))

    # XXX: duplicates are not stripped here, because this is an expensive
    #      operation that would be repeated one time per field.
    return authors


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
            'x': get_recid_from_ref(value.get('record')),
            'y': value.get('curated_relation')
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
