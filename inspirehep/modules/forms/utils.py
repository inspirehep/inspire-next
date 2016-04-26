# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA

"""Forms utilities."""

from __future__ import absolute_import, print_function


def filter_empty_helper(keys=None):
    """Remove empty elements from a list."""
    def _inner(elem):
        if isinstance(elem, dict):
            for k, v in elem.items():
                if (keys is None or k in keys) and v:
                    return True
            return False
        else:
            return bool(elem)
    return _inner


def filter_empty_elements(recjson, list_fields):
    """Filter empty fields."""
    for key in list_fields:
        recjson[key] = filter(
            filter_empty_helper(), recjson.get(key, [])
        )

    for k in recjson.keys():
        if not recjson[k]:
            del recjson[k]

    return recjson
