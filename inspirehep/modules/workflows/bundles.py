# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
"""Bundles for forms used across INSPIRE."""

from __future__ import absolute_import, division, print_function

from invenio_assets import NpmBundle
from invenio_assets.filters import RequireJSFilter

from inspirehep.modules.theme.bundles import js as _js

details_js = NpmBundle(
    "js/inspire_workflows_ui/holdingpen/app.js",
    output="gen/inspire-workflows.details.%(version)s.js",
    filters=RequireJSFilter(exclude=[_js]),
    npm={
        "angular-filter": "~0.5.8",
        "angular-xeditable": "~0.1.12",
        "angular-hotkeys-light": "~1.1.0"
    }
)
