# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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
#

from invenio.modules.deposit.bundles import js as _deposit_js, \
    styles as _deposit_styles
from invenio.base.bundles import jquery as _base_js

# '_' prefix indicates private variables, and prevents duplicated import by
# auto-discovery service of invenio

_deposit_js.contents.remove("js/deposit/init.js")
_deposit_js.contents += [
    'vendors/buckets/buckets.js'
]
_deposit_js.contents = ['js/deposit/inspire_init.js'] + _deposit_js.contents

_deposit_js.bower.update({
    'buckets': 'git://github.com/mauriciosantos/buckets.git',
    'bootstrap-multiselect': '~0.9.4'
})

_deposit_styles.contents += (
    'vendors/bootstrap-multiselect/css/bootstrap-multiselect.css',
    'css/deposit-inspire.css',
)
