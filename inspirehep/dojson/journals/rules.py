# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016, 2017 CERN.
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

"""DoJSON rules for journals."""

from __future__ import absolute_import, division, print_function

from dojson import utils
from idutils import normalize_issn

from .model import journals


@journals.over('issn', '^022..')
@utils.for_each_value
def issn(self, key, value):
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
        'comment': comment,
        'medium': medium,
        'value': issn,
    }


@journals.over('coden', '^030..')
@utils.for_each_value
def coden(self, key, value):
    return value.get('a')


@journals.over('journal_titles', '^130..')
@utils.for_each_value
def journal_titles(self, key, value):
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
    }


@journals.over('publisher', '^643..')
@utils.for_each_value
def publisher(self, key, value):
    return value.get('b')


@journals.over('short_titles', '^711..')
@utils.for_each_value
def short_titles(self, key, value):
    return {'title': value.get('a')}


@journals.over('title_variants', '^730..')
@utils.for_each_value
def title_variants(self, key, value):
    return {'title': value.get('a')}
