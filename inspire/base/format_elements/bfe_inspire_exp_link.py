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
"""BibFormat element - Prints HTML link to exp
"""
__revision__ = "$Id$"


def format_element(bfo, separator=', ', link="yes"):
    """Print Conference info as best is possible.

    @param link if yes (default) prints link to SPIRES conference info
    @param separator  separates multiple conferences
    """
    authors = bfo.fields('693__')
    output = []

    # Process authors to add link, highlight and format affiliation
    for exp in authors:
        if 'e' in exp:
            output.append('<a href="/search?ln=en&amp;cc=Experiments&amp;p=119__a%3A' +
                          exp['e'] +
                          '&amp;of=hd">' +
                          exp['e'] +
                          '</a>')

    return separator.join(output)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
