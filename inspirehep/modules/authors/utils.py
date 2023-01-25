# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Helper functions for authors."""

from __future__ import absolute_import, division, print_function

import re


_bai_parentheses_cleaner = \
    re.compile(r"(\([^)]*\))|(\[[^\]]*\])|(\{[^\}]*\})", re.UNICODE)
_bai_last_name_separator = re.compile(r"[,;]+", re.UNICODE)
_bai_names_separator = re.compile("[,;.=\-\s]+", re.UNICODE)
_bai_special_char_mapping = {'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue'}
_bai_nonletters = re.compile(r"[^\w\s]|\d", re.UNICODE)
_bai_spaces = re.compile(r"\s+", re.UNICODE)
_bai_particles = ["da", "de", "del", "den", "der",
                  "du", "van", "von", "het", "y"]
split_on_re = re.compile('[\.\s-]')
single_initial_re = re.compile('^\w\.$')


def _nonempty(words):
    words = [w.strip() for w in words]
    words = [w for w in words if len(w) >= 1]
    return words


def bai(name):
    # Remove content in parentheses
    name = _bai_parentheses_cleaner.sub("", name)

    # Get last name and initials
    names = _bai_last_name_separator.split(name, maxsplit=1)
    names = _nonempty(names)

    if len(names) == 1:
        names = _bai_spaces.split(name, maxsplit=1)
        names = _nonempty(names)

    if len(names) == 0:
        return ""

    elif len(names) == 2:
        last_name = names[0]
        initials = [w[0].upper()
                    for w in _bai_names_separator.split(names[1]) if w]

    else:
        last_name = names[0]
        initials = []

    # Asciify
    for char, replacement in _bai_special_char_mapping.items():
        last_name = last_name.replace(char, replacement)
        initials = [i.replace(char, replacement) for i in initials]

    initials = _nonempty(initials)

    # Capitalize words in last name
    words = _bai_names_separator.split(last_name)
    words = _nonempty(words)

    for i, w in enumerate(words):
        if w.lower() in _bai_particles and i < len(words) - 1:
            words[i] = w.lower()
        elif (all([c.isupper() or c == "'" for c in w]) or
              all([c.islower() or c == "'" for c in w])):
            words[i] = w.title()
        else:
            words[i] = w

    bai = "%s %s" % (" ".join(initials), " ".join(words))

    # Keep letters and spaces
    bai = _bai_nonletters.sub("", bai)
    bai = bai.strip()

    # Replace all spaces with .
    bai = _bai_spaces.sub(".", bai)

    return bai
