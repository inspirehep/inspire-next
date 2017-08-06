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

"""Various helpers for the overlay."""

from __future__ import absolute_import, division, print_function


def force_list(data):
    """Force ``data`` to become a list.

    You should use this method whenever you don't want to deal with the
    fact that ``NoneType`` can't be iterated over. For example, instead
    of writing::

        bar = foo.get('bar')
        if bar is not None:
            for el in bar:
                ...

    you can write::

        for el in force_list(foo.get('bar')):
            ...

    Args:
        data: any Python object.

    Returns:
        list: a list representation of ``data``.

    Examples:
        >>> force_list(None)
        []
        >>> force_list('foo')
        ['foo']
        >>> force_list(('foo', 'bar'))
        ['foo', 'bar']
        >>> force_list(['foo', 'bar', 'baz'])
        ['foo', 'bar', 'baz']

    """
    if data is None:
        return []
    elif not isinstance(data, (list, tuple, set)):
        return [data]
    elif isinstance(data, (tuple, set)):
        return list(data)
    return data


def maybe_int(el):
    """Return an ``int`` if possible, otherwise ``None``.

    Args:
        el: any Python object.

    Returns:
        Union[int, NoneType]: an ``int`` parsed from the object, or ``None``.

    Examples:
        >>> maybe_int('10')
        10

    """
    try:
        return int(el)
    except (TypeError, ValueError):
        pass
