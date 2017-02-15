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

"""Inspire Records"""

from __future__ import absolute_import, division, print_function

from datetime import datetime

import arrow
from elasticsearch.exceptions import NotFoundError

from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records.api import Record
from invenio_db import db

from inspirehep.utils.record_getter import (
    RecordGetterError,
    get_es_record_by_uuid
)


class InspireRecord(Record):

    """Record class that fetches records from DataBase."""

    def merge(self, other):
        """Redirect pidstore of current record to the other InspireRecord.

        :param other: The record that self(record) is going to be redirected.
        :type other: InspireRecord
        """
        pids_deleted = PersistentIdentifier.query.filter(PersistentIdentifier.object_uuid == self.id).all()
        pid_merged = PersistentIdentifier.query.filter(PersistentIdentifier.object_uuid == other.id).one()
        with db.session.begin_nested():
            for pid in pids_deleted:
                pid.redirect(pid_merged)
                db.session.add(pid)

    def delete(self):
        """Mark as deleted all pidstores for a specific record."""
        pids = PersistentIdentifier.query.filter(PersistentIdentifier.object_uuid == self.id).all()
        with db.session.begin_nested():
            for pid in pids:
                pid.delete()
                db.session.add(pid)

        self['deleted'] = True
        self.commit()

    def _delete(self, *args, **kwargs):
        super(InspireRecord, self).delete(*args, **kwargs)

    def commit(self, validators=None):
        """Override commit() to pass custom validators"""
        super(InspireRecord, self).commit(validators)


class ESRecord(InspireRecord):

    """Record class that fetches records from ElasticSearch."""

    @classmethod
    def get_record(cls, object_uuid, with_deleted=False):
        """Get record instance from ElasticSearch."""
        try:
            return cls(get_es_record_by_uuid(object_uuid))
        except RecordGetterError as e:
            if isinstance(e.cause, NotFoundError):
                # Raise this error so the interface will render a 404 page
                # rather than a 500
                raise PIDDoesNotExistError('es_record', object_uuid)
            else:
                raise

    @property
    def updated(self):
        """Get last updated timestamp."""
        if self.get('_updated'):
            return arrow.get(self['_updated']).naive
        else:
            return datetime.utcnow()
