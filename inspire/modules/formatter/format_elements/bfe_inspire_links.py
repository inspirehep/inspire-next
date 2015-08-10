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
""" BibFormat element - scans through all fields likely to create urls
(856, 773, etc) and creates and displays a list of those links.  Currently
does not include arXiv.
"""

from invenio.base.i18n import gettext_set_language
from invenio.base.globals import cfg
from invenio.legacy.bibdocfile.api import bibdocfile_url_to_bibdoc

if cfg.get('CFG_BASE_URL'):
    CFG_BASE_URL = cfg.get('CFG_BASE_URL')
else:
    CFG_BASE_URL = cfg.get('CFG_SITE_URL')


def format_element(bfo, default='', separator='; ', style='',
                   show_icons='no', prefix='', suffix=''):
    """Create html of links based on metadata.

    @param separator (separates instances of links)
    @param prefix
    @param suffix
    @param show_icons default = no
    @param style options CSS style for link
    """
    _ = gettext_set_language(bfo.lang)
    if style != "":
        style = 'class = "' + style + '"'

    links = []

    # KEKSCAN/CDS links
    identifiers = bfo.fields('035__')

    for ident in identifiers:
        if ident.get('9', '') == 'KEKSCAN' and ident.get('a', None) is not None:
            out = ident['a'].replace("-", "")
            links.append('<a href="http://www-lib.kek.jp/cgi-bin/img_index?' + out + '"> KEK scanned document </a>')

        if ident.get('9', '') == 'CDS' and ident.get('a', None) is not None:
            links.append('<a href="http://cds.cern.ch/record/' + ident['a'] + '"> CERN Document Server </a>')

    # ADS links
    identifiers = bfo.fields('037__')
    current_links = bfo.field('8564_y')

    for ident in identifiers:
        if ident.get('9', '') == 'arXiv' and not ("ADSABS" in current_links) and ident.get('a', None) is not None:
            links.append('<a href="http://adsabs.harvard.edu/cgi-bin/basic_connect?qsearch=' + ident.get('a', '') + '">ADS Abstract Service</a>')

    # links moved to new field 035
    urls = bfo.fields('035__')
    for url in urls:
        if "9" in url and "a" in url:
            if url["9"].lower() == "msnet":
                links.append('<a ' + style + ' href="http://www.ams.org/mathscinet-getitem?mr=' + url["a"] + '">AMS MathSciNet</a>')
            if url["9"].lower() == "zblatt":
                links.append('<a ' + style + ' href="http://www.zentralblatt-math.org/zmath/en/search/?an=' + url["a"] + '">zbMATH</a>')
            if url["9"].lower() == "euclid":
                links.append('<a ' + style + ' href="http://projecteuclid.org/euclid.cmp/=' + url["a"] + '">Project Euclid</a>')

    # now look for explicit URLs
    # might want to check that we aren't repeating things from above...
    # Note: excluding self-links
    urls = bfo.fields('8564_')
    allowed_doctypes = ["INSPIRE-PUBLIC", "SCOAP3", "PoS"]
    for url in urls:
        if url.get("y", "").lower() not in ("msnet", "zblatt", "euclid"):
            if '.png' not in url.get('u', '') and not \
               (url.get('y', '').lower().startswith("fermilab") and bfo.field("710__g").lower() in ('atlas collaboration', 'cms collaboration')):
                if url.get('y', '').upper() != "DURHAM":
                    if url.get("u", '') and \
                       url.get('y', 'Fulltext').upper() != "DOI" and not \
                       url.get('u', '').startswith(cfg.get('CFG_SITE_URL')):
                        links.append('<a ' + style
                                     + 'href="' + url.get("u", '') + '">'
                                     + _lookup_url_name(bfo, url.get('y', 'Fulltext')) + '</a>')
                    elif url.get("u", '').startswith(cfg.get('CFG_SITE_URL')) and \
                        (url.get("u", '').lower().endswith(".pdf") or
                         url.get("u", '').lower().endswith('.pdf?subformat=pdfa')) and \
                            bibdocfile_url_to_bibdoc(url.get('u')).doctype in allowed_doctypes:
                        (links.append('<a ' + style + 'href="' + url.get("u", '') + '">' +
                         _lookup_url_name(bfo, url.get('y', 'Fulltext')) + '</a>'))

    # put it all together
    if links:
        if show_icons.lower() == 'yes':
            img = '<img style="border:none" \
            src="%s/img/file-icon-text-12x16.gif" alt="%s"/>' \
            % (CFG_BASE_URL, _("Download fulltext"))
            links = [img + '<small>' + link + '</small>' for link in links]
        return prefix + separator.join(links) + suffix
    else:
        return default


def _lookup_url_name(bfo, abbrev=''):
    """Find the display name for the url, based on an abbrev in record.

    Input:  bfo, abbrev  (abbrev is PHRVA-D, etc)
    Output: display string  (Phys Rev D Server)
    """
    if abbrev is None:
        abbrev = ''
    return bfo.kb('WEBLINKS', abbrev, 'Link to ' + abbrev)


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
