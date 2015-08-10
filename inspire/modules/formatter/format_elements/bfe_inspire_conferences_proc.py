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
"""BibFormat element - Prints link to proceedings for conferences
"""

from invenio.legacy.search_engine import perform_request_search
from invenio.legacy.search_engine.utils import get_fieldvalues


def format_element(bfo, newline=False, show_doi=False):
    """Print link to proceedings if the proceedings exist.

    @param newline: if True, add <br /> at the end
    @param show_doi: if True, show DOI of the proceeding in brackets
    """
    cnum = str(bfo.field('111__g'))
    out = ""
    if not cnum:
        # something is wrong, return empty string
        return out
    search_result = perform_request_search(p="773__w:" + cnum + " and 980__a:proceedings")
    if search_result:
        if len(search_result) > 1:
            # multiple proceedings
            proceedings = []
            for i, recID in enumerate(search_result):
                # check for the DOI and put it in brackets in the output
                doi = get_fieldvalues(recID, '0247_a')
                if show_doi and doi:
                    proceedings.append('<a href="/record/%(ID)s">#%(number)s</a> (DOI: <a href="http://dx.doi.org/%(doi)s">%(doi)s</a>)'
                                       % {'ID': recID, 'number': i+1, 'doi': doi[0]})
                else:
                    proceedings.append('<a href="/record/%(ID)s">#%(number)s</a>' % {'ID': recID, 'number': i+1})
            out = 'Proceedings: '
            out += ', '.join(proceedings)
        elif len(search_result) == 1:
            # only one proceeding
            out += '<a href="/record/' + str(search_result[0]) + '">Proceedings</a>'
        if newline:
            out += '<br/>'
    return out


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
