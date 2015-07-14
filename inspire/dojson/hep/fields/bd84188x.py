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


@hep.over('url', '^856.[10_28]')
@utils.for_each_value
@utils.filter_values
def url(self, key, value):
    """URL to external resource."""
    return {
        'url': value.get('u'),
        'doc_string': value.get('w'),
        'description': value.get('y'),
        'material_type': value.get('3'),
        'comment': value.get('z'),
        'name': value.get('f'),
        'size': value.get('s'),
    }


@hep2marc.over('8564', 'url')
@utils.for_each_value
@utils.filter_values
def url2marc(self, key, value):
    """URL to external resource."""
    return {
        'u': value.get('url'),
        'w': value.get('doc_string'),
        'y': value.get('description'),
        '3': value.get('material_type'),
        'z': value.get('comment'),
        'f': value.get('name'),
        's': value.get('size'),
    }
