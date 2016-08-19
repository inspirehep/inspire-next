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

import langdetect

from ..model import hep, hep2marc

from inspirehep.dojson.utils import force_single_element
from inspirehep.utils.helpers import force_force_list


@hep.over('titles', '^(210|24[2567])[10_][0_]')
def titles(self, key, value):
    def is_main_title(key):
        return key.startswith('245')

    def is_translated_title(key):
        return key.startswith('242')

    titles = self.setdefault('titles', [])
    values = force_force_list(value)
    for val in values:
        title_obj = {
            'title': val.get('a'),
            'subtitle': force_single_element(val.get('b')),  # FIXME: #1484
            'source': val.get('9'),
        }
        if is_main_title(key):
            titles.insert(0, title_obj)
        elif is_translated_title(key):
            title = val.get('a')
            if title:
                lang = langdetect.detect(title)
                if lang:
                    title_obj['language'] = lang
                    self.setdefault('title_translations', []).append(title_obj)
        else:
            titles.append(title_obj)

    return titles


@hep2marc.over('246', '^titles$')
def titles2marc(self, key, value):
    def get_transformed_title(val):
        return {
            'a': val.get('title'),
            'b': val.get('subtitle'),
            '9': val.get('source'),
        }

    values = force_force_list(value)
    if values:
        # Anything but the first element is the main title
        self['245'] = [get_transformed_title(values[0])]
    return [get_transformed_title(value) for value in values[1:]]


@hep2marc.over('242', r'^title_translations$')
def title_translations2marc(self, key, value):
    def get_transformed_title(val):
        return {
            'a': val.get('title'),
            'b': val.get('subtitle'),
            '9': val.get('source'),
        }

    values = force_force_list(value)
    return [get_transformed_title(value) for value in values]
