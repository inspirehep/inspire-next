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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Models for crawler integration."""

from datetime import datetime

from enum import Enum

from invenio_ext.sqlalchemy import db

from sqlalchemy_utils.types import ChoiceType, UUIDType


class JobStatus(Enum):
    """Constants for possible status of any given PID."""

    __order__ = 'PENDING RUNNING FINISHED UNKNOWN'

    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    UNKNOWN = ''

    def __init__(self, value):
        """Hack."""

    def __eq__(self, other):
        """Equality test."""
        return self.value == other

    def __str__(self):
        """Return its value."""
        return self.value


class CrawlerJob(db.Model):

    """Represents a submitted crawler job."""

    __tablename__ = 'crawler_job'

    job_id = db.Column(UUIDType, primary_key=True, index=True)
    spider = db.Column(db.String(255), index=True)
    workflow = db.Column(db.String(255), index=True)
    status = db.Column(ChoiceType(JobStatus, impl=db.String(10)), nullable=False)
    scheduled = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)

    @classmethod
    def create(cls, job_id, spider, workflow, status=JobStatus.PENDING):
        """Create a new entry for a scheduled crawler job."""
        obj = cls(job_id=job_id,
                  spider=spider,
                  workflow=workflow,
                  status=status)
        db.session.add(obj)


__all__ = (
    'CrawlerJob',
)
