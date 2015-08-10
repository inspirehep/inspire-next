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
"""BibFormat element - Prints INSPIRE jobs contact name HEPNAMES search
"""

from datetime import datetime


def format_element(bfo, style="", separator=''):
    """Default format for the contact person link in the Jobs format.

    This link will point to a direct search in the HepNames database.

    @param style: CSS class of the link
    @param separator: the separator between names.
    """
    out = []
    fulladdress = bfo.fields("111__")
    sday = ''
    smonth = ''
    syear = ''
    fday = ''
    fmonth = ''
    fyear = ''
    printaddress = ''

    for printaddress in fulladdress:
        if 'd' in printaddress:
            out.append(printaddress['d'])
            break
        else:
            if 'x' in printaddress:
                sdate = printaddress['x']
                sday = sdate[-2:]
                smonth = sdate[5:7]
                syear = sdate[:4]
            if 'y' in printaddress:
                fdate = printaddress['y']
                fday = fdate[-2:]
                fmonth = fdate[5:7]
                fyear = fdate[:4]

    try:
        smonth = datetime.strptime(smonth, "%m").strftime("%b")
        fmonth = datetime.strptime(fmonth, "%m").strftime("%b")
    except ValueError:
        pass

    if printaddress in fulladdress:
        if 'd' not in printaddress:
            if syear == fyear:
                if smonth == fmonth:
                    # year matches and month matches
                    out.append(sday+'-'+fday+' '+fmonth+' '+fyear)
                else:
                    # year matches and month doesn't
                    out.append(sday + ' ' + smonth + ' - ' + fday + ' ' + fmonth + ' ' + fyear)
            if not syear == fyear and not smonth == fmonth:
                # year doesn't match and don't test month
                out.append(sday + ' ' + smonth + ' ' + syear + ' - ' + fday + ' ' + fmonth + ' ' + fyear)
    return separator.join(out)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
