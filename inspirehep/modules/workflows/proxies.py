# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""Extra models for workflows."""

from __future__ import absolute_import, division, print_function

import pkg_resources

from werkzeug.local import LocalProxy

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


@lru_cache()
def load_antikeywords():
    """Loads list of antihep keywords with cached gotcha."""
    antihep_keywords_list = []
    with open(pkg_resources.resource_filename('inspirehep', 'kbs/corepar.kb'), 'r') as kb_file:
        for line in kb_file:
            key = line.split('---')[0]
            if key and key not in antihep_keywords_list:
                antihep_keywords_list.append(key.strip())
    return antihep_keywords_list


antihep_keywords = LocalProxy(lambda: load_antikeywords())

__all__ = ('antihep_keywords', )
