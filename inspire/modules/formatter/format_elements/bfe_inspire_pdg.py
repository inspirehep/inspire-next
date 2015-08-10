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
"""BibFormat element - Prints HTML link to pdg
"""

from invenio.modules.knowledge.api import get_kb_mappings


__revision__ = "$Id$"


def format_element(bfo, separator=' | ', link="yes"):
    """Print Conference info as best is possible.

    @param link if yes (default) prints link to SPIRES conference info
    @param separator  separates multiple conferences
    """
    authors = bfo.fields('084__')
    output = []
    output1 = []
    pdgcount = 0
    link = ""
    pdgcode = ""

    # Process authors to add link, highlight and format affiliation
    for exp in authors:
        if exp.get('9') == 'PDG' and 'a' in exp:
            values = get_kb_mappings('PDG', key=exp['a'], match_type="e")
            pdgcode = exp['a']
            for ch in [':', '=']:
                if ch in pdgcode:
                    pdgcode = pdgcode.replace(ch, '/')
            if values:
                search_link = ('<a href="http://pdglive.lbl.gov/view/' +
                               pdgcode +
                               '">')
                if values[0]['value'] == "THE TEXT IS MISSING FOR THIS NODE.":
                    search_link += pdgcode + ' (Title Unknown)'
                else:
                    search_link += values[0]['value']
                search_link += '</a>'
                pdgcount += 1
                if pdgcount < 3:
                    output.append(search_link)
                else:
                    output1.append(search_link)

    if len(output1):
        link = """ | <a href="#" style="color:green;background:white;" onclick="toggle2('content', this)"><i>More</i></a>
<div id="content" style="display:none; padding-left:36px;">
%(content)s
</div>
<script type="text/javascript">
function toggle2(id, link) {
var e = document.getElementById(id);
if (e.style.display == '') {
e.style.display = 'none';
link.innerHTML = '<i>More</i>';
}
else
{
e.style.display = '';
link.innerHTML = '<i>Less</i>';
}
}
</script>
""" % {'content': separator.join(output1)}

    return separator.join(output) + link


def escape_values(bfo):
    """
    Check if output of this element should be escaped.

    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
