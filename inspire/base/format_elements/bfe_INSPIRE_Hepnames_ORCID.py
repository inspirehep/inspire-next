# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2014, 2015 CERN.
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
"""BibFormat element - Prints HepNames ORCID
"""


def format_element(bfo):
    """
    Prints HepNames ORCID from 035__a if 035__9 is ORCID.
    """
    bai = bfo.fields('035__')

    for item in bai:
        if '9' in item and item['9'] == 'ORCID' and 'a' in item:
            orcid = item['a']
            if "http" in orcid:
                return '<a href="%s">%s</a>' % (orcid, orcid)
            else:
                link = "http://orcid.org/" + orcid
                return '<a href="%s">%s</a>' % (link, orcid)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
