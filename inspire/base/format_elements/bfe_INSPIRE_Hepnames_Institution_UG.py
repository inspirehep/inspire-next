# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - Prints Hepnames Institutions UG
"""
__revision__ = "$Id$"

def format_element(bfo):
    """
    Prints Hepnames Institutions UG
    """
    authors = bfo.fields('371__')

    # Process authors to add link, highlight and format affiliation
    for author in authors:
        if author.has_key('r') and author['r'] == 'UG' and author.has_key('a'):
            return '<a href="/search?ln=en&amp;cc=Institutions&amp;ln=en&amp;cc=Institutions&amp;p=110__u%3A%22' \
            + author['a'] + '%22&amp;action_search=Search&amp;sf=&amp;so=d&amp;rm=&amp;rg=25&amp;sc=0&amp;of=hd">' \
            + author['a'] +'</a>'

    # Uncomment next line if default value must be returned
    # return 'whatever'

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
