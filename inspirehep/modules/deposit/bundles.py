# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from invenio_deposit.bundles import js as _deposit_js, \
    styles as _deposit_styles
from invenio_ext.assets import Bundle, RequireJSFilter
from invenio_base.bundles import jquery as _j, invenio as _i

# '_' prefix indicates private variables, and prevents duplicated import by
# auto-discovery service of invenio


_deposit_js.contents = ['js/deposit/inspire_init.js']

_deposit_js.bower.update({
    'bucketsjs': '1.98.1',
    'bootstrap-multiselect': '0.9.10',
    'readmore': '*',
})


# Bundle for deposit stats page

js_stats = Bundle(
    "js/deposit/stats/init.js",
    output="deposit_stats.js",
    filters=RequireJSFilter(exclude=[_j, _i]),
    weight=51,
    bower={
        'highcharts-release': 'latest',
    }
)

_deposit_styles.contents += (
    'vendors/bootstrap-multiselect/dist/css/bootstrap-multiselect.css',
    'css/deposit-inspire.css',
)
