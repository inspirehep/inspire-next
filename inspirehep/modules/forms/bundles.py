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

"""Bundles for forms used across INSPIRE."""

from __future__ import absolute_import, division, print_function

from invenio_assets import NpmBundle
from invenio_assets.filters import RequireJSFilter

from inspirehep.modules.theme.bundles import js as _js


js = NpmBundle(
    "js/forms/inspire-form-init.js",
    output="gen/inspire-form.%(version)s.js",
    filters=RequireJSFilter(exclude=[_js]),
    npm={
        "eonasdan-bootstrap-datetimepicker": "~4.15.35",
        "typeahead.js": "~0.10.5",
        "bootstrap-multiselect": "~0.9.13",
        "moment": "~2.11.2",
    }
)

css = NpmBundle(
    "scss/forms/form.scss",
    "node_modules/eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.css",
    "node_modules/typeahead.js-bootstrap-css/typeaheadjs.css",
    "node_modules/bootstrap-multiselect/dist/css/bootstrap-multiselect.css",
    output='gen/inspire-form.%(version)s.css',
    depends='scss/forms/*.scss',
    filters="node-scss, cleancss",
    npm={
        "typeahead.js-bootstrap-css": "~1.2.1"
    }
)
