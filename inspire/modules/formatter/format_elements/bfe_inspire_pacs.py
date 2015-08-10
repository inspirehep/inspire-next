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
"""BibFormat element - Prints HTML links to PACS with translation from KB
"""

from urllib import urlencode
from invenio.modules.knowledge.api import get_kb_mappings


def format_element(bfo, separator=' | ', link="yes"):
    """Print PACS info as best is possible.

    @param link if yes (default) prints link to search for this item in Inspire
    @param separator separates multiple items
    """
    fields = bfo.fields('084__')

    output = []
    output1 = []
    pacs_count = 0
    link = ""

    for item in fields:
        if item.get('2') == 'PACS':
            pacs_code = item.get('a')
            if pacs_code:
                pacs_kb_mapping = get_kb_mappings('PACS', key=pacs_code, match_type="e")
                title = 'Translation not available'
                if pacs_kb_mapping:
                    title = pacs_kb_mapping[0]['value']
                search_link = ("<a href='/search?" +
                               urlencode({'p': '084__:"' + pacs_code + '"'}) +
                               "' title='" +
                               title +
                               "'>" +
                               pacs_code +
                               "</a>")
                if pacs_count < 25:
                    output.append(search_link)
                else:
                    output1.append(search_link)
            pacs_count += 1

            if len(output1):
                link = """ | <a href="#" onclick="toggle2('content', this); return false;" style="color:green;background:white;"><i>More</i></a>
<div id="content" style="display:none; padding-left:42px;">
%(content)s
</div>
<script type="text/javascript">
function toggle2(id, link) {
var e = document.getElementById(id);
if (e.style.display == '') {
    e.style.display = 'none';
    link.innerHTML = '<i>More</i>';
}
else {
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
