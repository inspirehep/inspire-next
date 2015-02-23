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
"""Bibformat element - Return an HTML link to ArXiv.
"""


def format_element(bfo, separator=", "):
    """Return a HTML link to arXiv.org for each arXiv report-number."""
    fields = bfo.fields('037__')
    fields.extend(bfo.fields('088__'))
    out = []

    for field in fields:
        if '9' in field and field['9'] == 'arXiv':
            temp_out = ""
            # if new arxiv
            if ':' in field['a']:
                temp_out = '<a href="http://arXiv.org/abs/' + field['a'] + '">' + field['a'] + '</a>'
                if 'c' in field:
                    temp_out += ' [' + field['c'] + ']'
            # else old arxiv
            else:
                temp_out = '<a href="http://arXiv.org/abs/' + field['a'] + '">' + field['a'] + '</a>'

            if 'arXiv:' in field['a']:
                temp_out += ' | <a href="http://arXiv.org/pdf/' + field['a'][6:] + '.pdf">PDF</a>'
            else:
                temp_out += ' | <a href="http://arXiv.org/pdf/' + field['a'] + '.pdf">PDF</a>'
            out.append(temp_out)

    return separator.join(out)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
