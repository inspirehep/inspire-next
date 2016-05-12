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
from inspirehep.dojson import utils as inspire_dojson_utils

from idutils import normalize_issn

from inspirehep.dojson.utils import strip_empty_values

from ..model import journals


@journals.over('issn', '^022..')
@utils.for_each_value
def issn(self, key, value):
    """ISSN and its medium with additional comment."""
    issn = {}
    if 'a' in value:
        issn['value'] = normalize_issn(value.get('a', ''))
    else:
        return issn
    if 'b' in value:
        issn['medium'] = value.get('b', '').lower()
        if issn['medium'] == 'print':
            pass
        elif issn['medium'] == 'online':
            pass
        elif 'electronic' in issn['medium']:
            issn['medium'] = 'online'
            issn['comment'] = 'electronic'
        elif 'ebook' in issn['medium']:
            issn['medium'] = 'online'
            issn['comment'] = 'ebook'
        elif 'hardcover' in issn['medium']:
            issn['medium'] = 'print'
            issn['comment'] = 'hardcover'
        else:
            issn['comment'] = issn['medium']
            issn['medium'] = ''

    return strip_empty_values(issn)


@journals.over('coden', '^030..')
@utils.for_each_value
def coden(self, key, value):
    """CODEN Statement."""
    return value.get("a")


@journals.over('publisher', '^643..')
@utils.for_each_value
def publisher(self, key, value):
    """Publisher."""
    return value.get('b')


@journals.over('titles', '^130..')
@utils.for_each_value
def titles(self, key, value):
    """Title used in breadcrum and html title."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b')
    }


@journals.over('short_titles', '^711..')
@utils.for_each_value
def titles_short(self, key, value):
    """Short titles."""
    return {
        'title': value.get('a'),
    }


@journals.over('title_variants', '^730..')
@utils.for_each_value
def title_variants(self, key, value):
    """Title variants."""
    return {
        'title': value.get('a'),
    }
