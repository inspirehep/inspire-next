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
"""BibFormat element - Prints notes
"""
__revision__ = "$Id$"


def format_element(bfo, note_suffix, separator=', '):
    """Print the supervisor of a thesis with a given seperator."""
    notes = []
    supervisor = bfo.fields('701__a')

    for item in supervisor:
        if item.find(',') > 0:
            comma = item.find(',')
            item = item[comma+2:] + " " + item[:comma]
        notes.append('<a href="/search?ln=en&amp;cc=HepNames&amp;p=fin+a+' + item + '&of=hd">' + item + '</a>')
    return separator.join(notes)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
