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
"""WTForm filters implementation.

Filters can be applied to incoming form data, after process_formdata() has run.

See more information on:
http://wtforms.simplecodes.com/docs/1.0.4/fields.html#wtforms.fields.Field
"""

from __future__ import absolute_import, division, print_function

import six


def strip_prefixes(*prefixes):
    """Return a filter function that removes leading prefixes from a string."""

    def _inner(value):
        """Remove a leading prefix from string."""
        if isinstance(value, six.string_types):
            for prefix in prefixes:
                if value.lower().startswith(prefix):
                    return value[len(prefix):]
        return value

    return _inner


def strip_string(value):
    """Remove leading and trailing spaces from string."""
    if isinstance(value, six.string_types):
        return value.strip()
    else:
        return value


def clean_empty_list(value):
    """Created to clean a list produced by Bootstrap multi-select."""
    if value in ([u"None"], [u""]):
        return []
    return value
