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

import six

from dojson import utils

from ..model import jobs
from ...utils import classify_rank, force_single_element, get_record_ref


@jobs.over('date_closed', '^046..')
def date_closed(self, key, value):
    """Date the job was closed."""
    def _contains_email(val):
        return '@' in val

    def _contains_url(val):
        return 'www' in val or 'http' in val

    el = force_single_element(value)

    deadline_date = force_single_element(el.get('i'))
    if deadline_date:
        self['deadline_date'] = deadline_date

    closing_date = None
    closing_info = force_single_element(el.get('l'))
    if closing_info:
        if _contains_email(closing_info):
            if 'reference_email' in self:
                self['reference_email'].append(closing_info)
            else:
                self['reference_email'] = [closing_info]
        elif _contains_url(closing_info):
            if 'urls' in self:
                self['urls'].append({'value': closing_info})
            else:
                self['urls'] = [{'value': closing_info}]
        else:
            closing_date = closing_info

    return closing_date


@jobs.over('contact_details', '^270..')
@utils.for_each_value
def contact_details(self, key, value):
    name = value.get('p')
    email = value.get('m')

    return {
        'name': name if isinstance(name, six.string_types) else None,
        'email': email if isinstance(email, six.string_types) else None,
    }


@jobs.over('continent', '^043..')
def continent(self, key, value):
    """Continent"""
    return value.get('a')


@jobs.over('experiments', '^693..')
@utils.for_each_value
def experiments(self, key, value):
    """Contact person."""
    return value.get('e')


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
        'record': get_record_ref(recid, 'isntitutions'),
        'name': value.get('a'),
    }


@jobs.over('description', '^520..')
def description(self, key, value):
    """Contact person."""
    return value.get('a')


@jobs.over('position', '^245..')
def position(self, key, value):
    """Contact person."""
    self.setdefault('breadcrumb_title', value.get('a'))
    return value.get('a')


@jobs.over('ranks', '^656..')
@utils.for_each_value
def ranks(self, key, value):
    """Ranks."""
    self.setdefault('_ranks', [])
    self.setdefault('ranks', [])

    values = utils.force_list(value)
    for el in values:
        _ranks = utils.force_list(el.get('a'))
        for _rank in _ranks:
            self['_ranks'].append(_rank)
            self['ranks'].append(classify_rank(_rank))
