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
"""BibFormat element - Hep Erratum info
"""

import cgi


def format_element(bfo):
    """Print Hep Erratum info."""
    pubinfos = bfo.fields('773__')

    if not pubinfos:
        return ""

    # Process pubnotes
    newline = "<br />"
    out = []
    for pubinfo in pubinfos:
        volume = cgi.escape(pubinfo.get('v', ''))
        number = cgi.escape(pubinfo.get('n', ''))
        pages = cgi.escape(pubinfo.get('c', ''))
        doi = bfo.field('0247_a') or pubinfo.get('a', '')
        if 'p' in pubinfo:
            tmpout = []
            if not (volume or number or pages or doi):
                tmpout.append("Submitted to:")
            tmpout.append(pubinfo.get('p', None))
            tmpout.append(pubinfo.get('v', None))
            if 'y' in pubinfo:
                tmpout.append('(%s)' % (pubinfo.get('y'),))
            tmpout.append(pubinfo.get('c', None))
            out.append("<strong>%s</strong>" % (" ".join([a for a in tmpout if a]),))
        if 'x' in pubinfo and ("In *".lower() in pubinfo['x'].lower() or "Also in *".lower() in pubinfo['x'].lower()):
            out.append("<small>%s</small>" % (pubinfo['x'],))

    return newline.join(out)


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
