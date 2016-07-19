# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Helpers for handling pubnote parsing."""

import re

from inspirehep.utils.helpers import force_force_list

_RE_2_CHARS = re.compile(r'[a-z].*[a-z]', re.I)


def split_page_artid(page_artid):
    """Split page_artid into page_start/end and artid."""
    page_start = None
    page_end = None
    artid = None

    if not page_artid:
        return None, None, None

    # TODO use force_force_list when it's in inspirehep.utils.
    page_artid_l = force_force_list(page_artid)

    for page_artid in page_artid_l:
        if page_artid:
            if '-' in page_artid:
                # if it has a dash it's a page range
                page_range = page_artid.split('-')
                if len(page_range) == 2:
                    page_start, page_end = page_range
                else:
                    artid = page_artid
            elif _RE_2_CHARS.search(page_artid):
                # if it has 2 ore more letters it's an article ID
                artid = page_artid
            elif len(page_artid) >= 5:
                # it it is longer than 5 digits it's an article ID
                artid = page_artid
            else:
                if artid is None:
                    artid = page_artid
                if page_start is None:
                    page_start = page_artid

    return page_start, page_end, artid


def split_pubnote(pubnote_str):
    """Split pubnote into journal information."""
    title, volume, page_start, page_end, artid = (None, None, None, None, None)
    parts = pubnote_str.split(',')

    if len(parts) > 2:
        title = parts[0]
        volume = parts[1]
        page_start, page_end, artid = split_page_artid(parts[2:])

    return title, volume, page_start, page_end, artid
