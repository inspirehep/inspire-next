# -*- coding: utf-8 -*-
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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Model for Audit."""

from datetime import datetime

from invenio.ext.sqlalchemy import db
from invenio.ext.sqlalchemy.utils import session_manager


class Audit(db.Model):

    __tablename__ = "audit_logging"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Date that the action was taken
    created = db.Column(db.DateTime, default=datetime.now, nullable=False)

    user_id = db.Column(db.Integer, default=0, nullable=False)
    object_id = db.Column(db.Integer, default=0, nullable=False)

    # Score from model, action taken, recommendation from the model
    score = db.Column(db.Float, default=0, nullable=False)
    user_action = db.Column(db.Text, default="", nullable=False)
    decision = db.Column(db.Text, default="", nullable=False)

    source = db.Column(db.Text, default="", nullable=False)
    action = db.Column(db.Text, default="", nullable=False)

    @session_manager
    def save(self):
        """Save object to persistent storage."""
        db.session.add(self)
