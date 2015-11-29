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

from ..model import journals


@journals.over('issn', '^022..')
def issn(self, key, value):
    """ISSN Statement."""
    return value.get("a")


@journals.over('coden', '^030..')
def coden(self, key, value):
    """CODEN Statement."""
    return value.get("a")


@journals.over('title', '^130..')
def title(self, key, value):
    """Title Statement."""
    return value.get('a')


@journals.over('breadcrumb_title', '^130..')
def breadcrumb_title(self, key, value):
    """Title used in breadcrum and html title."""
    return value.get('a')


@journals.over('publisher', '^643..')
def publisher(self, key, value):
    """Title used in breadcrum and html title."""
    return value.get('b')


@journals.over('short_title', '^711..')
def short_title(self, key, value):
    """Title Statement."""
    return value.get('a')


@journals.over('name_variants', '^730..')
@utils.for_each_value
def name_variants(self, key, value):
    """Variants of the name."""
    return value.get('a')


@journals.over('urls', '^856.[10_28]')
@utils.for_each_value
def urls(self, key, value):
    """URLs."""
    return {
        'urls': value.get('u'),
        'doc_string': value.get('w')
    }
