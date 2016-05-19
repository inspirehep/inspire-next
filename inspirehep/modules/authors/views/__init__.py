# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 331, Boston, MA 02111-1307, USA.

"""View blueprints for Author module."""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)

from .forms import blueprint as forms_blueprint
from .holdingpen import blueprint as holdingpen_blueprint
from .publications import blueprint as publications_blueprint

blueprints = [
    forms_blueprint,
    holdingpen_blueprint,
    publications_blueprint,
]
