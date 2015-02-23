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
"""BibFormat element - Prints the page and date of article
"""
from invenio.modules.formatter.format_elements.bfe_field import format_element as get_field
from bfe_inspire_date import format_element as get_date_element


def format_element(bfo, separator=" - ", page_suffix=" pages"):
    """Print the page and date of article with a given seperator."""
    date = get_date_element(bfo)
    pages = get_field(bfo, "300a", "1")
    out = []
    if date:
        out.append(str(date))
        # Let us see if pages are not empty, if yes, we're done
        if pages != '':
            # We have a date and page so add page info with suffix
            out.append(separator)
            out.append(pages + page_suffix)
    elif pages != '':
        # We have only page info
        out.append(pages + page_suffix)
    return "".join(out)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
