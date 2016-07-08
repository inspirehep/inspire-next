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

from ..model import hep, hep2marc


@hep.over('title_translations', '^242[10_][0_]')
@hep.over('titles_old', '^247[10_][10_]')
@utils.for_each_value
@utils.filter_values
def title_translations_old(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'source': value.get('9'),
        'title': value.get('a'),
        'subtitle': value.get('b')
    }


@hep2marc.over('210', '^title_variations$')
@hep2marc.over('242', '^title_translations$')
@hep2marc.over('247', '^titles_old$')
@utils.for_each_value
@utils.filter_values
def title_trans_var_old2marc(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
        '9': value.get('source'),
    }


@hep.over('title_variations', '^210[10_][0_]')
def title_variations(self, key, value):
    """Title variations."""
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
        cleaned_titles = existing + out
        return cleaned_titles

    if 'title_variations' in self:
        titles = get_value(self['title_variations'])
    else:
        titles = get_value([])

    return titles


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
        cleaned_titles = existing + out
        return cleaned_titles

    if 'titles' in self:
        titles = get_value(self['titles'])
    else:
        titles = get_value([])

    return titles


@hep2marc.over('245', '^titles$')
def titles2marc(self, key, value):
    """Title Statement for 245/246."""
    arxiv_246_title = None
    titles = []

    for title in utils.force_list(value):
        transformed_title = {
            'a': title.get('title'),
            'b': title.get('subtitle'),
            '9': title.get('source'),
        }
        if title.get('source', '').lower() == 'arxiv':
            arxiv_246_title = transformed_title
        else:
            titles.append(transformed_title)

    if len(titles) == 0 and arxiv_246_title is not None:
        titles.append(arxiv_246_title)
    if arxiv_246_title is not None:
        self['246'] = arxiv_246_title
    return titles
