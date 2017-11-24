# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Inspire bundles."""

from __future__ import absolute_import, division, print_function

from invenio_assets import NpmBundle

# Used when ASSETS_DEBUG is False - like production
almondjs = NpmBundle(
    "node_modules/almond/almond.js",
    "js/settings.js",
    filters="uglifyjs",
    output="gen/almond.%(version)s.js",
    npm={
        "almond": "~0.3.1",
        "hogan.js": "~3.0.2",
        "requirejs-hogan-plugin": "~0.3.1"
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
        "requirejs": "~2.1.22",
    }
)

js = NpmBundle(
    "js/inspire_base_init.js",
    filters="requirejs",
    depends=(
        "js/**/*.js"
    ),
    output="gen/inspirehep.%(version)s.js",
    npm={
        "jquery": "~1.9.1",
        "jquery-ui": "~1.10.5",
        "clipboard": "~1.5.8",
        "flightjs": "~1.5.0",
        "angular": "~1.4.8",
        "readmore-js": "~2.1.0",
        "impact-graphs": "git+https://git@github.com/inspirehep/impact-graphs.git",
        "inspirehep-typeahead-search-js": "git+https://github.com/inspirehep/inspirehep-typeahead-search-js.git",
    }
)

detailedjs = NpmBundle(
    "js/detailed_record_init.js",
    filters="requirejs",
    output="gen/detailed_record.%(version)s.js",
    npm={
        "d3": "~3.5.16",
        "datatables.net": "~1.10.11",
        "datatables.net-bs": "~1.10.11",
    }
)

css = NpmBundle(
    "scss/inspirehep.scss",
    filters="node-scss, cleancss",
    output="gen/inspirehep.%(version)s.css",
    depends="scss/**/*.scss",
    npm={
        "bootstrap-sass": "~3.3.5",
        "font-awesome": "~4.4.0",
    }
)

landing_page_css = NpmBundle(
    "scss/landing_page.scss",
    filters="node-scss, cleancss",
    output="gen/inspirehep.landing.%(version)s.css",
    depends="scss/landing_page.scss"
)

holding_pen_css = NpmBundle(
    "node_modules/angular-xeditable/dist/css/xeditable.css",
    "scss/holding-pen/holding-pen.scss",
    filters="node-scss, cleancss",
    output="gen/inspirehep.holding.%(version)s.css",
    depends="scss/**/*.scss"
)
