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

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

from inspirehep.dojson.utils import (
    classify_rank,
    get_record_ref
)

import six

from dojson import utils

from ..model import jobs


@jobs.over('date_closed', '^046..')
def date_closed(self, key, value):
    """Date the job was closed."""
    value = utils.force_list(value)
    closed_date = None
    deadline_date = None
    for val in value:
        if val.get('i'):
            deadline_date = val.get('i')
        if val.get('l'):
            if "@" in val.get('l'):
                # Its an email
                if "reference_email" in self:
                    self["reference_email"].append(val.get('l'))
                else:
                    self["reference_email"] = [val.get('l')]
            elif "www" in val.get('l') or "http" in val.get('l'):
                # Its a URL
                if "urls" in self:
                    self["urls"].append(val.get('l'))
                else:
                    self["urls"] = [val.get('l')]
            else:
                closed_date = val.get('l')
    if deadline_date:
        self['deadline_date'] = deadline_date
    return closed_date


@jobs.over('continent', '^043..')
@utils.for_each_value
def continent(self, key, value):
    """Continent"""
    return value.get('a')


@jobs.over('institution', '^110..')
@utils.for_each_value
@utils.filter_values
def institution(self, key, value):
    """Institution info."""
    curated_relation = False
    recid = None
    if value.get('z') and value.get('z').isdigit():
        curated_relation = True
        recid = int(value.get('z'))
    return {
        'curated_relation': curated_relation,
        'record': get_record_ref(recid, 'institutions'),
        'name': value.get('a'),
    }


@jobs.over('position', '^245..')
def position(self, key, value):
    """Position."""
    return value.get('a')


@jobs.over('contact_details', '^270..')
@utils.for_each_value
def contacts(self, key, value):
    """Contacts details."""
    name = value.get('p')
    email = value.get('m')

    return {
        'name': name if isinstance(name, six.string_types) else None,
        'email': email if isinstance(email, six.string_types) else None
    }


@jobs.over('description', '^520..')
def description(self, key, value):
    """Job description"""
    return value.get('a')


@jobs.over('ranks', '^656..')
def rank(self, key, value):
    """Jobs rank casted to enums"""
    ranks = []
    _ranks = []
    values = utils.force_list(value)
    for val in values:
        raw_rank = val.get('a')
        if isinstance(raw_rank, six.string_types):
            _ranks.append(raw_rank)
            ranks.append(classify_rank(raw_rank))
        elif isinstance(raw_rank, tuple):
            for rank in raw_rank:
                _ranks.append(rank)
                ranks.append(classify_rank(rank))
        else:
            pass

    self['_ranks'] = _ranks
    return ranks


@jobs.over('experiments', '^693..')
@utils.for_each_value
def experiments(self, key, value):
    """Related experiments"""
    return value.get('e')
