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


@hep.over('title_variation', '^210[10_][0_]')
@utils.for_each_value
@utils.filter_values
def title_variation(self, key, value):
    """Title variation."""
    return {
        'title_variation': value.get('a')
    }


@hep2marc.over('210', 'title_variation')
@utils.for_each_value
@utils.filter_values
def title_variation2marc(self, key, value):
    """Title variation."""
    return {
        'a': value.get('title_variation'),
    }


@hep.over('title_translation', '^242[10_][0_]')
@utils.for_each_value
@utils.filter_values
def title_translation(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'title_translation': value.get('a'),
        'subtitle': value.get('b')
    }


@hep2marc.over('242', 'title_translation')
@utils.for_each_value
@utils.filter_values
def title_translation2marc(self, key, value):
    """Translation of Title by Cataloging Agency."""
    return {
        'a': value.get('title_translation'),
        'b': value.get('subtitle'),
    }


@hep.over('title', '^245[10_][0_]')
@utils.filter_values
def title(self, key, value):
    """Title Statement."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
        'source': value.get('9'),
    }


@hep2marc.over('245', 'title')
@utils.for_each_value
@utils.filter_values
def title2marc(self, key, value):
    """Title Statement."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
        '9': value.get('source'),
    }


@hep.over('title_arxiv', '^246[1032_][_103254768]')
@utils.for_each_value
@utils.filter_values
def title_arxiv(self, key, value):
    """Varying Form of Title."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
        'source': value.get('9'),
    }


@hep2marc.over('246', 'title_arxiv')
@utils.for_each_value
@utils.filter_values
def title_arxiv2marc(self, key, value):
    """Varying Form of Title."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
        '9': value.get('source'),
    }


@hep.over('title_old', '^247[10_][10_]')
@utils.for_each_value
@utils.filter_values
def title_old(self, key, value):
    """Former Title."""
    return {
        'title': value.get('a'),
        'subtitle': value.get('b'),
        'source': value.get('9'),
    }


@hep2marc.over('247', 'title_old')
@utils.for_each_value
@utils.filter_values
def title_old2marc(self, key, value):
    """Former Title."""
    return {
        'a': value.get('title'),
        'b': value.get('subtitle'),
        '9': value.get('source'),
    }
