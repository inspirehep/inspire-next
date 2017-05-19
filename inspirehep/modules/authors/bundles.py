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

"""Bundles for author forms."""

from __future__ import absolute_import, division, print_function

from flask_assets import Bundle
from invenio_assets import NpmBundle
from invenio_assets.filters import RequireJSFilter

from inspirehep.modules.theme.bundles import js as _js

update_css = Bundle(
    "scss/authors/authors-update-form.scss",
    output='gen/inspire-author-update.%(version)s.css',
    depends='scss/forms/*.scss',
    filters="node-scss, cleancss"
)

js = NpmBundle(
    'js/authors/app.js',
    filters='requirejs',
    depends=(
        'js/authors/author.js',
        'js/authors/profile.js',
        'js/authors/publications.js',
        'js/authors/statistics.js'
    ),
    output="gen/authors.%(version)s.js"
)

updatejs = NpmBundle(
    "js/authors/author_form_init.js",
    output="gen/authors-submission-form.%(version)s.js",
    filters=RequireJSFilter(exclude=[_js]),
)
