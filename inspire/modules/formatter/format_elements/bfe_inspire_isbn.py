# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
"""BibFormat element - Print ISBN
"""

__revision__ = "$Id$"


def format_element(bfo, separator=", "):
    """Return the ISBN of the record."""
    isbn_names = bfo.fields("020__")
    isbn_ready = []
    for pair in isbn_names:
        if 'a' in pair:
            if 'b' in pair:
                isbn_ready.append("%s (%s)" % (pair['a'], pair['b'],))
            else:
                isbn_ready.append(pair['a'])

    return separator.join(isbn_ready)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
