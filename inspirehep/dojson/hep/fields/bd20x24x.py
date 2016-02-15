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

    if isinstance(value, list):
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


@hep.over('titles', '^245[10_][0_]')
def titles(self, key, value):
    """Title Statement."""
    def get_value(existing):
        if not isinstance(value, list):
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
        return get_value(self['titles'])
    else:
        return get_value([])


@hep.over('breadcrumb_title', '^245[10_][0_]')
def breadcrumb_title(self, key, value):
    """Title used in breadcrumb and html title."""
    if 'breadcrumb_title' in self:
        return self['breadcrumb_title']
    else:
        if isinstance(value, list):
            value = value[0]
        return value.get('a')


@hep2marc.over('245', '^titles$')
def titles2marc(self, key, value):
    """Title Statement."""
    if len(value) == 1:
        return [{
            'a': value[0].get('title'),
            'b': value[0].get('subtitle'),
            '9': value[0].get('source'),
        }]
    else:
        for title in value:
            if not title.get('source') or title.get('source', '').lower() != "arxiv":
                    return [{
                        'a': title.get('title'),
                        'b': title.get('subtitle'),
                        '9': title.get('source'),
                    }]


@hep.over('titles', '^246[1032_][_103254768]')
def title_arxiv(self, key, value):
    """Varying Form of Title."""
    def get_value(existing):
        if not isinstance(value, list):
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
        return get_value(self['titles'])
    else:
        return get_value([])


@hep2marc.over('246', '^titles$')
def title_arxiv2marc(self, key, value):
    """Varying Form of Title."""
    if not isinstance(value, list):
        values = [value]
    else:
        values = value
    for val in values:
        if val.get('source', '') and val.get('source', '').lower() == "arxiv":
            return {
                'a': val.get('title'),
                'b': val.get('subtitle'),
                '9': val.get('source'),
            }


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
