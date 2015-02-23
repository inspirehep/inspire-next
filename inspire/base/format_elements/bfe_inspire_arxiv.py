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
"""BibFormat element - Links record to arXiv metadata when possible"""


def format_element(bfo, links="no", category="yes", mirrors="yes"):
    """Provide arXiv number in format for display or links.

    @param links yes->display links to arXiv only no(default)-> display value of arxiv number only
    @param category -> displays category in '[]' after number (only if not redundant)
    @param mirrors -> defautl yes  only relevant if links=yes
    """
    arxiv = get_arxiv(bfo, category="no")

    if len(arxiv) == 0:
        return

    out = ''
    if links == 'yes':
        # Take only first one
        arxiv_ref = arxiv[0]
        out += '''
<a href="http://arXiv.org/abs/%(ref)s">Abstract</a> and
<a href="http://arXiv.org/ps/%(ref)s">Postscript</a>
 and <a href="http://arXiv.org/pdf/%(ref)s">PDF</a> from arXiv.org''' % {'ref': arxiv_ref}

        if mirrors.lower() == 'yes':
            out += '''
 (mirrors:
<a href="http://au.arXiv.org/abs/%(ref)s">au</a>

<a href="http://br.arXiv.org/%(ref)s">br</a>
<a href="http://cn.arXiv.org/abs/%(ref)s">cn</a>
<a href="http://de.arXiv.org/abs/%(ref)s">de</a>
<a href="http://es.arXiv.org/abs/%(ref)s">es</a>
<a href="http://fr.arXiv.org/abs/%(ref)s">fr</a>
<a href="http://il.arXiv.org/abs/%(ref)s">il</a>
<a href="http://in.arXiv.org/abs/%(ref)s">in</a>
<a href="http://it.arXiv.org/abs/%(ref)s">it</a>
<a href="http://jp.arXiv.org/abs/%(ref)s">jp</a>
<a href="http://kr.arXiv.org/abs/%(ref)s">kr</a>
<a href="http://ru.arXiv.org/abs/%(ref)s">ru</a>
<a href="http://tw.arXiv.org/abs/%(ref)s">tw</a>
<a href="http://uk.arXiv.org/abs/%(ref)s">uk</a>
<a href="http://aps.arXiv.org/abs/%(ref)s">aps</a>
<a href="http://lanl.arXiv.org/abs/%(ref)s">lanl</a>)''' % {'ref': arxiv_ref}

    else:
        # print only value
        out = ', '.join(get_arxiv(bfo, category))

    return out


def get_arxiv(bfo, category="yes"):
    """Take a bfo and returns a list of arXiv ids found within the report numbers."""
    primary_report_numbers = bfo.fields('037__')
    additional_report_numbers = bfo.fields('088__')
    report_numbers = primary_report_numbers
    report_numbers.extend(additional_report_numbers)

    arxiv = [num.get('a', '') for num in report_numbers if num.get('9') == 'arXiv'
             or num.get('s') == 'arXiv']

    if category == "yes":
        cats = [num.get('c', '') for num in report_numbers if num.get('9') == 'arXiv'
                or num.get('s') == 'arXiv']
        arxiv = map(append_cat, arxiv, cats)

    return arxiv


def get_cats(bfo):
    """Return a list of categories (in same order as numbers from get_arxiv)."""
    primary_report_numbers = bfo.fields('037__')
    additional_report_numbers = bfo.fields('088__')
    report_numbers = primary_report_numbers
    report_numbers.extend(additional_report_numbers)

    cat = [num.get('c', '') for num in report_numbers if num.get('9') == 'arXiv'
           or num.get('s') == 'arXiv']

    return cat


def append_cat(number, cat):
    import re
    if not cat:
        return number
    if not re.match(cat, number):
        return number+' [' + cat + ']'
    return number


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
