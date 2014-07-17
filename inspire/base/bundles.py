# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

"""Base bundles."""

from invenio.ext.assets import Bundle
from invenio.modules.search.bundles import \
    search_js as _search_js

inspire_css = Bundle(
    'less/inspire.less',
    output = 'inspire.css',
    weight = 00,
    filters = 'less',
)

index_js = Bundle(
    'js/jquery.feeds.min.js',
    'js/moment.min.js',
    output = 'index.js',
    weight = 60,
    bower = {
        "jquery-feeds": "git://github.com/camagu/jquery-feeds.git",
        "moment": "2.7.0",
    },
)

_search_js.contents += (
    'js/search/invenio_with_spires_typeahead_configuration.js',
)