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

from dojson import utils

from inspirehep.dojson import utils as inspire_dojson_utils

from ..model import hep, hep2marc


@hep.over('title_variation', '^210[10_][0_]')
def title_variation(self, key, value):
    """Title variation."""
    def get_value(value):
        return value.get('a')

    title_variation_list = self.get('title_variation', [])

    if isinstance(value, (tuple, list)):
        for element in value:
            title_variation_list.append(get_value(element))
    else:
        title_variation_list.append(get_value(value))

    return inspire_dojson_utils.remove_duplicates_from_list(title_variation_list)


@hep2marc.over('210', '^title_variation$')
@utils.for_each_value
@utils.filter_values
def title_variation2marc(self, key, value):
    """Title variation."""
    return {
        'a': value,
    }


@hep.over('title_translation', '^242[10_][0_]')
@utils.for_each_value
@utils.filter_values
def title_translation(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b')
    }


@hep2marc.over('242', '^title_translation$')
@utils.for_each_value
@utils.filter_values
def title_translation2marc(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
    }


@hep.over('titles', '^24[56][10_][0_]')
def titles(self, key, value):
    """Title Statement."""
    def get_value(existing):
        if not isinstance(value, (tuple, list)):
            values = [value]
        else:
            values = value
        out = []
        for val in values:
            out.append({
                'title': val.get('a'),
                'subtitle': val.get('b'),
                'source': val.get('9'),
            })
        return existing + out


    if 'titles' in self:
        titles = get_value(self['titles'])
    else:
        titles = get_value([])

    if titles and 'breadcrumb_title' not in self:
        self['breadcrumb_title'] = titles[0]['title']

    return titles


@hep2marc.over('245', '^titles$')
def titles2marc(self, key, value):
    """Title Statement for 245/246."""
    title_245 = None
    arxiv_246 = None

    for title in utils.force_list(value):
        transformed_title = {
            'a': title.get('title'),
            'b': title.get('subtitle'),
            '9': title.get('source'),
        }
        if title.get('source') is not None and title.get('source', '').lower() == "arxiv":
            arxiv_246 = transformed_title
        elif title_245 is None:
            title_245 = transformed_title

    if arxiv_246 is not None:
        self['246'] = arxiv_246
    return [title_245]


@hep.over('titles_old', '^247[10_][10_]')
@utils.for_each_value
@utils.filter_values
def titles_old(self, key, value):
    """Former Title."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
        'source': value.get('9'),
    }


@hep2marc.over('247', '^titles_old$')
@utils.for_each_value
@utils.filter_values
def titles_old2marc(self, key, value):
    """Former Title."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
        '9': value.get('source'),
    }
