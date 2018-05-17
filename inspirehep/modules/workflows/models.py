# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Extra models for workflows."""

from __future__ import absolute_import, division, print_function

from datetime import datetime

from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.types import UUIDType

from invenio_db import db


class WorkflowsAudit(db.Model):

    __tablename__ = "workflows_audit_logging"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Date that the action was taken
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("accounts_user.id", ondelete='CASCADE'),
        nullable=True,
        index=True,
    )
    object_id = db.Column(
        db.Integer,
        db.ForeignKey("workflows_object.id", ondelete='CASCADE'),
        nullable=False,
        index=True,
    )

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


class WorkflowsPendingRecord(db.Model):

    __tablename__ = "workflows_pending_record"

    workflow_id = db.Column(
        db.Integer,
        db.ForeignKey("workflows_object.id", ondelete='CASCADE'),
        primary_key=True,
        nullable=False,
    )
    record_id = db.Column(db.Integer, nullable=False)


class Timestamp(object):
    """Timestamp model mix-in with fractional seconds support.
    SQLAlchemy-Utils timestamp model does not have support for fractional
    seconds.
    """

    created = db.Column(
        db.DateTime(),
        default=datetime.utcnow,
        nullable=True,
    )
    updated = db.Column(
        db.DateTime(),
        default=datetime.utcnow,
        nullable=True,
    )


@db.event.listens_for(Timestamp, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    """Update `updated` property with current time on `before_update` event."""
    target.updated = datetime.utcnow()


class WorkflowsRecordSources(db.Model, Timestamp):

    __tablename__ = 'workflows_record_sources'
    __table_args__ = (
        db.PrimaryKeyConstraint('record_uuid', 'source'),
    )

    record_uuid = db.Column(
        UUIDType,
        db.ForeignKey('records_metadata.id', ondelete='CASCADE'),
        nullable=False,
    )

    source = db.Column(
        postgresql.ENUM('arxiv', 'submitter', 'publisher', name='source_enum'),
        nullable=False,
    )

    json = db.Column(
        postgresql.JSONB(),
        default=lambda: dict(),
    )
