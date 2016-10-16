# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Proxy objects for easier access to application objects."""

from flask import current_app
from werkzeug.local import LocalProxy


def _get_current_relations():
    """Return current state of the relations extension."""
    return current_app.extensions['inspire-relations']


def _get_current_graph_db():
    """Return current Neo4j client."""
    return _get_current_relations().graph_db

def _get_current_db_session():
    """Return current Neo4j db session."""
    return _get_current_relations().current_session


current_db_session = LocalProxy(_get_current_db_session)
current_graph_db = LocalProxy(_get_current_graph_db)
current_relations = LocalProxy(_get_current_relations)
