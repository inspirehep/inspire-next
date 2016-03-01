# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""UI for Invenio-Search."""

from flask_assets import Bundle
from invenio_assets import NpmBundle

css = Bundle(
    'scss/search/search.scss',
    filters='scss, cleancss',
    output='gen/search.%(version)s.css'
)

js = NpmBundle(
    'node_modules/angular/angular.js',
    'js/search/app.js',
    filters='requirejs',
    depends=('node_modules/invenio-search-js/dist/*.js', ),
    output='gen/search.%(version)s.js',
    npm={
        "almond": "~0.3.1",
        'angular': '~1.4.7',
        'invenio-search-js': '~0.1.0'
    },
)
