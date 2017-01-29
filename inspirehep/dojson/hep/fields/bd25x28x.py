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


@hep.over('edition', '^250..')
@utils.for_each_value
def edition(self, key, value):
    """Edition Statement."""
    return {'edition': value.get('a')}


@hep2marc.over('250', 'edition')
@utils.for_each_value
def edition2marc(self, key, value):
    """Edition Statement."""
    return {'a': value.get('edition'), }


@hep.over('imprints', '^260[_23].')
@utils.for_each_value
def imprints(self, key, value):
    """Publication, Distribution, etc. (Imprint)."""
    return {
        'place': value.get('a'),
        'publisher': value.get('b'),
        'date': value.get('c'),
    }


@hep2marc.over('260', 'imprints')
@utils.for_each_value
def imprints2marc(self, key, value):
    """Publication, Distribution, etc. (Imprint)."""
    return {
        'a': value.get('place'),
        'b': value.get('publisher'),
        'c': value.get('date'),
    }


@hep.over('preprint_date', '^269..')
def preprint_date(self, key, value):
    """Preprint info."""
    if isinstance(value, (tuple, list)):
        return min(elem['c'] for elem in value if 'c' in elem)
    return value.get('c')


@hep2marc.over('269', 'preprint_date')
@utils.for_each_value
def preprint_date2marc(self, key, value):
    """Preprint info."""
    return {'c': value, }
