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

from __future__ import absolute_import, division, print_function

from dojson import utils

from ..model import hep, hep2marc


@hep.over('number_of_pages', '^300..')
def number_of_pages(self, key, value):
    """Page number."""
    try:
        result = value.get('a')
        if isinstance(result, list):
            return int(result[0])
        else:
            return int(result)
    except (TypeError, IndexError):
        return None


@hep2marc.over('300', 'number_of_pages')
@utils.for_each_value
def number_of_pages2marc(self, key, value):
    """Page number."""
    return {
        'a': str(value),
    }
