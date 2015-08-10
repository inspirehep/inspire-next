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
"""BibFormat element - Prints DOI
"""


def format_element(bfo, tag="0247_,773__", separator=", ", link_prefix='http://dx.doi.org/'):
    """Return an HTML link to the DOI."""
    tags = tag.split(",")
    output = []
    for a_tag in tags:
        fields = bfo.fields(a_tag)
        for field in fields:
            if (a_tag == "773__" or field.get('2', 'DOI') == 'DOI') and 'a' in field:
                output.append('<a href="' + link_prefix + field['a'] + '">' + field['a'] + '</a>')
    return separator.join(set(output))


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
