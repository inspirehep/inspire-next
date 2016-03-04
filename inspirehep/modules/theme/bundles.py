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

from invenio_assets import NpmBundle

almondjs = NpmBundle(
    'node_modules/almond/almond.js',
    'js/settings.js',
    filters='uglifyjs',
    output="gen/almond.%(version)s.js",
    npm={
        "almond": "~0.3.1",
        "hogan.js": "~3.0.2",
        "requirejs-hogan-plugin": "~0.3.1",
    }
)

# require.js is only used when:
#
#  - ASSETS_DEBUG is True
#  - REQUIREJS_RUN_IN_DEBUG is not False
requirejs = NpmBundle(
    "node_modules/requirejs/require.js",
    "js/settings.js",
    output="gen/require.%(version)s.js",
    filters="uglifyjs",
    npm={
        "requirejs": "latest",
    }
)

js = NpmBundle(
    'js/inspire_base_init.js',
    filters='requirejs',
    depends=(
        'js/*.js',
        'js/inspire/*.js',
        'js/inspire/filters/*.js',
        'node_modules/invenio-search-js/dist/*.js',
    ),
    output="gen/inspirehep.%(version)s.js",
    npm={
        "jquery": "~1.9.1",
        "toastr": "~2.1.2",
        "clipboard": "~1.5.8",
        "flightjs": "~1.5.0",
        "angular": "~1.4.9",
        "angular-sanitize": "~1.4.9"
    }
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
