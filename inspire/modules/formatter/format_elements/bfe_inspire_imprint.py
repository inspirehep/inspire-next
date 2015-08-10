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
"""BibFormat element - Prints document imprint
"""

__revision__ = "$Id$"


def format_element(bfo):
    """Print imprint.

    @see place.py, publisher.py, date.py, reprints.py
    """
    places_1 = bfo.fields('269__a')
    publishers_1 = bfo.fields('269__b')
    date_1 = bfo.field('269__c')

    places_2 = bfo.fields('260__a')
    publishers_2 = bfo.fields('260__b')
    date_2 = bfo.field('260__c')

    pagination = bfo.field('300__a')
    corporate_names = bfo.fields('931__a')
    publisher_infos = bfo.fields('933__')

    out = ""

##     for place in places_1:
##         if place != "sine loco":
##             out += place + ' '

##     for publisher in publishers_1:
##         if publisher != "sine nomine":
##             out += ' :' + publisher + ', '

    if date_1:
        out += date_1
    elif date_2:
        out += date_2


##     for place in places_2:
##         if place != "sine loco":
##             out += place + ' '

##     for publisher in publishers_2:
##         if publisher != "sine nomine":
##             out += ' :' + publisher + ', '

    if pagination:
        if date_1:
            out += '. '
        out += pagination + ' '

    if corporate_names:
        for corporate_name in corporate_names:
            out += corporate_name + ' '
    elif publisher_infos:
        for publisher_info in publisher_infos:
            if 'a' in publisher_info:
                out += publisher_info['a'] + ': ' + \
                       publisher_info.get('b', '') + '. ' +\
                       publisher_info.get('l', '')

    return out
