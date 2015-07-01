# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 CERN.
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
"""BibFormat element - return link to ADS author page from HepNames record
"""


def format_element(bfo):
    """
    create link to author page at ADS from HepNames author data
    """

    import re
    re_last_first = re.compile(
        '^(?P<last>[^,]+)\s*,\s*(?P<first_names>[^\,]*)(?P<extension>\,?.*)$')
    re_initials = re.compile(r'(?P<initial>\w)([\w`\']+)?.?\s*', re.UNICODE)

    ADSURL = 'http://adsabs.harvard.edu/cgi-bin/author_form?'
    author = bfo.field('100__a')

    lastname = ''
    firstnames = ''
    initial = ''

    if author:
        amatch = re_last_first.search(author)
        if amatch:
            lastname = amatch.group('last')
            firstnames = amatch.group('first_names')
    if firstnames:
        initialmatch = re_initials.search(unicode(firstnames, 'utf8'))
        firstnames = re.sub('\s+', '+', firstnames)
        if initialmatch:
            initial = initialmatch.group('initial')

    link = ''
    if lastname:
        lastname = re.sub('\s+', '+', lastname)
        link = "%sauthor=%s,+%s&fullauthor=%s,+%s" % \
               (ADSURL, lastname, initial, lastname, firstnames)
    else:
        link = "%sauthor=%s" % (ADSURL, bfo.field('100__q'))

    return link


# pylint: disable=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """

    return 0
# pylint: enable=W0613
