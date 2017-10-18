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
import itertools

import arrow
from elasticsearch.exceptions import NotFoundError
from flask import current_app

from invenio_files_rest.models import Bucket
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record
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

    def _create_bucket(self, location=None, storage_class=None):
        """Create file bucket for workflow object."""
        if location is None:
            location = current_app.config[
                'RECORDS_DEFAULT_FILE_LOCATION_NAME'
            ]
        if storage_class is None:
            storage_class = current_app.config[
                'RECORDS_DEFAULT_STORAGE_CLASS'
            ]

        bucket = Bucket.create(
            location=location,
            storage_class=storage_class
        )
        return bucket

    def attach_file(self, file_name, file):
        """Attach the file ``file`` to the record's files properties,
        updating the record's metadata..

        The file is attached only if there is a key in ``documents`` or
        ``figures`` which key match ``file_name``.
        Then. the name of the file is changed adding the record's
        ``control_number``as prefix. This change is reflected in
        the record's metadata too.

        Args:
            file_name(string): the name of the file to attach. It must be a
                key of ``documents`` or ``figures``.
            file(file): the file to attach to the file.

        Return:
            (string): the new file's key.

        Raise:
            ValueError in case ``file_name`` is not in record's documents and
                figures.

        Example:
            >>with open(my_file) as stream:
                record.attach_file('NewFile', stream)

        """

        control_number = self.get('control_number')
        normalized_file_name = u'{}_{}'.format(control_number, file_name)

        for attachment in itertools.chain(
                self.get('documents', []),
                self.get('figures', [])
        ):
            if attachment['key'] == file_name:
                #
                self.files[normalized_file_name] = file
                attachment['key'] = normalized_file_name
                attachment['url'] = '/api/files/{bucket}/{key}'.format(
                    bucket=self.files[normalized_file_name].bucket_id,
                    key=normalized_file_name
                )
                return normalized_file_name
        # ignore other files
        return None


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
