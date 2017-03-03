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

from __future__ import absolute_import, division, print_function


def calculate_h_index(citations):
    """
    Calculate the h-index of a citation dictionary.

    An author has h-index X if she has X papers with at least X citations each.
    See: https://en.wikipedia.org/wiki/H-index.

    :param citations: a dictionary in the format {recid: citation_count}
    :return: h-index of the dictionary of citations.
    """
    length = len(citations)

    histogram = [0] * (length + 1)
    for _, count in citations.items():
        histogram[min(count, length) if count else 0] += 1

    sum_ = 0
    for i, count in reversed(list(enumerate(histogram))):
        sum_ += count
        if sum_ >= i:
            return i

    return 0


def calculate_i10_index(citations):
    """
    Calculate the i10-index of a citation dictionary.

    An author has i10-index X if she has X papers with at least 10 citations
    each. See: https://en.wikipedia.org/wiki/H-index#i10-index

    :param citations: a dictionary in the format {recid: citation_count}
    :return: i10-index of the dictionary of citations.
    """
    return len([_ for _, count in citations.items() if count >= 10])
