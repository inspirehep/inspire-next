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


@hep.over('thesis_supervisor', '^701..')
@utils.for_each_value
@utils.filter_values
def thesis_supervisor(self, key, value):
    """The thesis supervisor."""
    return {
        'full_name': value.get('a'),
        'INSPIRE_id': value.get('g'),
        'external_id': value.get('j'),
        'affiliation': value.get('u')
    }


@hep2marc.over('701', 'thesis_supervisor')
@utils.for_each_value
@utils.filter_values
def thesis_supervisor2marc(self, key, value):
    """The thesis supervisor."""
    return {
        'a': value.get('full_name'),
        'g': value.get('INSPIRE_id'),
        'j': value.get('external_id'),
        'u': value.get('affiliation'),
    }


@hep.over('collaboration', '^710[10_2][_2]')
@utils.for_each_value
@utils.filter_values
def collaboration(self, key, value):
    """Added Entry-Corporate Name."""
    return {
        'collaboration': value.get('g')
    }


@hep2marc.over('710', 'collaboration')
@utils.for_each_value
@utils.filter_values
def collaboration2marc(self, key, value):
    """Added Entry-Corporate Name."""
    return {
        'g': value.get('collaboration'),
    }
