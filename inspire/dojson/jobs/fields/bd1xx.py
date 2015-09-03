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

from ..model import jobs


@jobs.over('acquisition_source', '^(037|270)..')
def acquisition_source(self, key, value):
    """Submission information aggregated from various sources."""
    result = {
        "method": "submission"
    }
    if key.startswith('037'):
        if "JOBSUBMIT" in value.get('a'):
            result["submission_number"] = value.get('a')
    elif key.startswith('270'):
        if value.get('m'):
            result["email"] = value.get('m')
    if "acquisition_source" in self:
        self["acquisition_source"].update(result)
        return self["acquisition_source"]
    else:
        return result


@jobs.over('contact_person', '^270..')
def contact_person(self, key, value):
    """Contact person."""
    return value.get('p')


@jobs.over('contact_email', '^270..')
def contact_email(self, key, value):
    """Contact email."""
    return value.get('m')


@jobs.over('reference_email', '^270..')
def reference_email(self, key, value):
    """Contact email."""
    return value.get('o')


@jobs.over('date_closed', '^046..')
def date_closed(self, key, value):
    """Date the job was closed."""
    return value.get('l')


@jobs.over('deadline_date', '^046..')
def deadline_date(self, key, value):
    """Date of job deadline."""
    return value.get('i')


@jobs.over('continent', '^043..')
def continent(self, key, value):
    """Contact person."""
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
    return {
        # 'curated_relation': value.get('a'),
        # 'recid': value.get('c')
        'name': value.get('a'),
    }


@jobs.over('description', '^520..')
def description(self, key, value):
    """Contact person."""
    return value.get('a')


@jobs.over('position', '^245..')
def position(self, key, value):
    """Contact person."""
    return value.get('a')


@jobs.over('research_area', '^65017')
@utils.for_each_value
def research_area(self, key, value):
    """Contact person."""
    return value.get('a')


@jobs.over('rank', '^656..')
@utils.for_each_value
def rank(self, key, value):
    """Contact person."""
    return value.get('a')


@jobs.over('urls', '^856.[10_28]')
@utils.for_each_value
def urls(self, key, value):
    """Contact person."""
    return value.get('u')
