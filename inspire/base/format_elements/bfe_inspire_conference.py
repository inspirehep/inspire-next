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
"""BibFormat element - Prints HTML link to talk
"""

__revision__ = "$Id$"


def format_element(bfo, separator=', ', link="yes"):
    """Print Conference info as best is possible.

    @param link if yes (default) prints link to SPIRES conference info
    @param separator  separates multiple conferences
    """
    from invenio.legacy.search_engine import perform_request_search

    confs = []
    confs = bfo.fields('773')
    output = []
    for conf in confs:
        note = ''
        if conf.get('w'):
            cnum = conf['w'].replace("/", "-")
            search_result = perform_request_search(p="111__g:" + cnum, c="Conferences")
            if search_result:
                recID = list(search_result)[0]
                conf_name = '<a class="conflink" href = "/record/' +\
                            str(recID) + '">' + cnum + '</a>'
            else:
                conf_name = cnum
            if conf.get('t'):
                note += conf['t'] + ' Conference: ' + conf_name
            else:
                note += 'Conference: ' + conf_name
            # Do not display 773_x when it refers on book chapters
            if conf.get('x') and not("In *".lower() in conf.get('x').lower() or
                                     "Also in *".lower() in conf.get('x').lower()):
                note += ' (' + conf['x'] + ')'
            if conf.get('c') and not conf.get('p'):
                # Only display pages from 773__c field, when there is no 773__p field
                # because when 773__p field exists, 773__c is already displayed in
                # bfe_INSPIRE_Hep_Erratum element (and we don't want to repeat it)
                note += ', p.' + conf['c']

        if len(note) > 0:
            output.append(note)

    return separator.join(output)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
