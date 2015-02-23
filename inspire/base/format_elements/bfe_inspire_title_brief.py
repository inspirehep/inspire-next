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
"""BibFormat element - Print titles in the most flexible reasonable fashion
"""


def format_element(bfo, highlight="no", force_title_case="no", brief="no", esctitle='0', oldtitles="no"):
    """
    Print a title, with optional subtitles, and optional highlighting.

    @param highlight highlights the words corresponding to search query if set to 'yes'
    @param force_title_case caps First Letter of Each World if set to 'yes'
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
        if brief == "no" and 'b' in title:
            out += ' : ' + title['b']

    # Concatenate any old titles (a) and subtitles(b)
    if oldtitles == "yes":
        for old_title in old_titles:
            out += "<br /><b><i>" + old_title.get('a') + '</i></b>'
            if brief == "no" and 'b' in old_title:
                out += ' : ' + old_title['b']

    # Hilight matching words if requested
    if highlight == 'yes':
        from invenio.modules.formatter import utils
        out = utils.highlight(out, bfo.search_pattern,
                              prefix_tag="<span style='font-weight: bolder'>",
                              suffix_tag='</span>')

    # Force title casing if requested and check if title is allcaps
    if force_title_case.lower() == "yes" and (out.upper() == out or out.find('THE ') >= 0):
        # .title() too dumb; don't cap 1 letter words
        out = ' '.join([word.capitalize() for word in out.split(' ')])

    return out


# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
