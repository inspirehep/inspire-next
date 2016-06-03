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
from idutils import normalize_issn

from ..model import journals
from ...utils import strip_empty_values


@journals.over('issn', '^022..')
@utils.for_each_value
@utils.filter_values
def issn(self, key, value):
    """ISSN, its medium and an additional comment."""
    try:
        issn = normalize_issn(value['a'])
    except KeyError:
        return {}

    b = value.get('b', '').lower()
    if 'online' == b:
        medium = 'online'
        comment = ''
    elif 'print' == b:
        medium = 'print'
        comment = ''
    elif 'electronic' in b:
        medium = 'online'
        comment = 'electronic'
    elif 'ebook' in b:
        medium = 'online'
        comment = 'ebook'
    elif 'hardcover' in b:
        medium = 'print'
        comment = 'hardcover'
    else:
        medium = ''
        comment = b

    return {
        'medium': medium,
        'value': issn,
        'comment': comment,
    }


@journals.over('coden', '^030..')
@utils.for_each_value
def coden(self, key, value):
    """CODEN Statement."""
    return value.get("a")


@journals.over('title', '^130..')
def title(self, key, value):
    """Title Statement."""
    self.setdefault('breadcrumb_title', value.get('a'))
    return value.get('a')


@journals.over('publisher', '^643..')
@utils.for_each_value
def publisher(self, key, value):
    """Title used in breadcrum and html title."""
    return value.get('b')


@journals.over('short_title', '^711..')
@utils.for_each_value
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
