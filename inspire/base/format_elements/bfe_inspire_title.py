# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007 CERN.
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
"""BibFormat element - Print titles in the most flexible reasonable fashion
"""


def format_element(bfo, brief="no", esctitle='1', oldtitles="no"):
    """
    Prints a title, with optional subtitles, and optional highlighting.

    @param brief If yes, skip printing subtitles; if no, print complete title:subtitle
    @param esctitle How should escaping of titles in the database be handled?
    @param oldtitles Whether to show old titles in output
    """

    out = ''
    esctitle = int(esctitle)

    titles = bfo.fields('245__', esctitle)
    old_titles = bfo.fields('246__', esctitle)

    # Concatenate all the regular titles (a) and (optionally) subtitles (b)
    for title in titles:
        out += title.get('a', '')
        if brief == "no" and title.has_key('b'):
            out += ' : ' + title['b']

    # Concatenate any old titles (a) and subtitles(b)
    if oldtitles == "yes":
        for old_title in old_titles:
            out += "<br /><b><i>" + old_title.get('a') + '</i></b>'
            if brief == "no" and old_title.has_key('b'):
                out += ' : ' + old_title['b']

    return out


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613