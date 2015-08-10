# -*- coding: utf-8 -*-
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.
"""Inspire bundles."""

from invenio.ext.assets import Bundle, RequireJSFilter
from invenio.base.bundles import jquery as _j, invenio as _i

js = Bundle(
    'js/inspire_base_init.js',
    output='base.js',
    filters=RequireJSFilter(exclude=[_j, _i]),
    weight=20,
)

# index_js = Bundle(
#     'vendors/jquery-feeds/dist/jquery.feeds.js',
#     'vendors/moment/moment.js',
#     output='index.js',
#     filters="requirejs",
#     weight=60,
#     bower={
#         "jquery-feeds": "git://github.com/camagu/jquery-feeds.git",
#     },
# )

# '_' prefix indicates private variables, and prevents duplicated import by
# auto-discovery service of invenio

from invenio.base.bundles import styles as _base_styles

#FIXME variables.less is already imported in inspire.less so there should be
#no need to add it here to the contents. If it is not added, the depends=
#parameter takes no effect and modifications to the file don't trigger
#bundle refresh.
_base_styles.contents += (
    'less/inspire.less',
    'less/accounts/settings/account-settings.less',
    'less/base/variables.less',
    'less/base/header.less',
    'less/base/footer.less',
    'less/base/panels.less',
    'less/base/helpers.less',
    'less/base/sticky-footer.less',
    'less/base/list-group.less',
    'less/base/core.less',
    'less/accounts/login.less',
    'less/search/index.less',
    'less/feedback/button.less',
    'less/feedback/modal.less',
    'less/format/brief-results.less',
    'less/workflows/workflows.less',
)

to_remove = ["less/base.less",
             "less/user-menu.less",
             "less/sticky-footer.less",
             "less/footer.less"]

for elem in to_remove:
    _base_styles.contents.remove(elem)

from invenio.modules.search.bundles import js as _search_js

_search_js.contents += (
    'js/search/invenio_with_spires_typeahead_configuration.js',
    'js/search/search_results.js',
    # 'js/search/search_box.js',
)

from invenio.modules.formatter.bundles import css as _formatter_css

_formatter_css.contents += (
    'css/formatter/templates_detailed_inspire.css',
)
