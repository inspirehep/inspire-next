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

"""Authors bundles."""

from invenio.ext.assets import Bundle, RequireJSFilter
from invenio.base.bundles import jquery as _j, invenio as _i

css = Bundle(
    "css/authors/profile_page.css",
    "vendors/datatables-bootstrap3/BS3/assets/css/datatables.css",
    "vendors/datatables-responsive/css/dataTables.responsive.css",
    "vendors/bootstrap-switch/dist/css/bootstrap3/bootstrap-switch.css",
    filters='less,cleancss',
    output="authors.css",
    weight=51,
    bower={
        "datatables": "latest",
        "datatables-bootstrap3": "latest",
        "datatables-responsive": "latest"
    })

js = Bundle(
    "js/authors/profile_page.js",
    output="authors.js",
    filters=RequireJSFilter(exclude=[_j, _i]),
    weight=51,
    bower={
        "bootstrap-switch": "latest",
        "datatables-bootstrap3": "latest",
        "datatables-responsive": "latest",
        "flight": "latest",
        "flot": "latest",
        "flot-axislabels": "latest",
        "flot.tooltip": "latest",
        "flot.orderbars": "latest",
        "growraf": "latest",
        "hogan": "latest",
        "readmore": "latest"
    })
