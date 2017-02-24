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


@hep.over('book_series', '^490[10_].')
@utils.for_each_value
def book_series(self, key, value):
    """Book Series."""
    return {
        'title': value.get('a'),
        'volume': value.get('v'),
    }


@hep2marc.over('490', 'book_series')
@utils.for_each_value
def book_series2marc(self, key, value):
    """Book Series."""
    return {
        'a': value.get('title'),
        'v': value.get('volume'),
    }
