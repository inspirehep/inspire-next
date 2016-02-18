# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Inspire bundles."""

from __future__ import absolute_import, print_function

from flask_assets import Bundle
from invenio_assets import NpmBundle

js = Bundle(
    NpmBundle(
        'node_modules/almond/almond.js',
        'js/settings.js',
        filters='uglifyjs',
        npm={
            "almond": "~0.3.1",
            "hogan": "latest",
            "requirejs-hogan-plugin": "latest",
            "jquery": "~1.9.1",
            "toastr": "latest",
            # "jQuery-menu-aim": "latest", # Not on npm :(
            "clipboard": "latest",
            "flightjs": "~1.5.0"
        }
    ),
    Bundle(
        'js/inspire_base_init.js',
        filters='requirejs',
    ),
    filters='jsmin',
    output="gen/inspirehep.%(version)s.js",
)

css = NpmBundle(
    'scss/inspirehep.scss',
    filters='scss, cleancss',
    output='gen/inspirehep.%(version)s.css',
    depends='scss/**/*.scss',
    npm={
        "bootstrap-sass": "~3.3.5",
        "font-awesome": "~4.4.0",
    }
)

# detailed_record_styles = Bundle(
#     "less/format/detailed-record.less",
#     "less/format/abstract.less",
#     "vendors/datatables/media/css/dataTables.bootstrap.css",
#     output="detailed-record.css",
#     depends=[
#         "less/format/detailed-record.less"
#     ],
#     filters="less,cleancss",
#     weight=60,
# )

# detailed_record_js = Bundle(
#     "js/detailed_record_init.js",
#     output="detailed_record.js",
#     filters=RequireJSFilter(exclude=[_j, _i]),
#     weight=51,
#     bower={
#         "datatables": "1.10.10"
#     }
# )

# brief_result_styles = Bundle(
#     "less/format/brief-results.less",
#     "less/format/abstract.less",
#     output="brief-results.css",
#     depends=[
#         "less/format/brief-results.less"
#     ],
#     filters="less,cleancss",
#     weight=60,
# )

# collection_landing_page_styles = Bundle(
#     "less/search/collection.less",
#     output="collection.css",
#     depends=[
#         "less/search/collection.less"
#     ],
#     filters="less,cleancss",
#     weight=60,
# )