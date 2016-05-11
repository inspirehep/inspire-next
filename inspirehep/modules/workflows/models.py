# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Extra models for workflows."""

from __future__ import absolute_import, print_function

from datetime import datetime

from invenio_db import db


class WorkflowsAudit(db.Model):

    __tablename__ = "workflows_audit_logging"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Date that the action was taken
    created = db.Column(db.DateTime, default=datetime.now, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("accounts_user.id"), nullable=True)
    object_id = db.Column(db.Integer, db.ForeignKey("workflows_object.id"), nullable=False)

    # Score from model, action taken, recommendation from the model
    score = db.Column(db.Float, default=0, nullable=False)
    user_action = db.Column(db.Text, default="", nullable=False)
    decision = db.Column(db.Text, default="", nullable=False)

    source = db.Column(db.Text, default="", nullable=False)
    action = db.Column(db.Text, default="", nullable=False)

    def save(self):
        """Save object to persistent storage."""
        with db.session.begin_nested():
            db.session.add(self)
