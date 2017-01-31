# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.
"""Fixtures for collection definitions."""

from __future__ import absolute_import, division, print_function

from flask import current_app

from invenio_collections.models import Collection
from invenio_db import db


def init_collections():
    """Init default collections."""
    for collection in current_app.config['INSPIRE_COLLECTIONS_DEFINITION']:
        c = Collection(name=collection['name'], dbquery=collection['query'])
        db.session.add(c)
    db.session.commit()
