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

"""Models for Migrator."""

from __future__ import absolute_import, division, print_function

import re

from datetime import datetime
from zlib import compress, decompress, error

from invenio_db import db
from sqlalchemy.ext.hybrid import hybrid_property

from .utils import get_collection_from_marcxml


class LegacyRecordsMirror(db.Model):
    __tablename__ = 'legacy_records_mirror'

    __table_args__ = (
        db.Index('ix_legacy_records_mirror_valid_collection', 'valid', 'collection'),
    )

    recid = db.Column(db.Integer, primary_key=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    _marcxml = db.Column('marcxml', db.LargeBinary, nullable=False)
    valid = db.Column(db.Boolean, default=None, nullable=True)
    _errors = db.Column('errors', db.Text(), nullable=True)
    collection = db.Column(db.Text(), default='')

    re_recid = re.compile('<controlfield.*?tag=.001.*?>(?P<recid>\d+)</controlfield>')

    @hybrid_property
    def marcxml(self):
        """marcxml column wrapper to compress/decompress on the fly."""
        try:
            return decompress(self._marcxml)
        except error:
            # Legacy uncompress data?
            return self._marcxml

    @marcxml.setter
    def marcxml(self, value):
        self._marcxml = compress(value)

    @hybrid_property
    def error(self):
        return self._errors

    @error.setter
    def error(self, value):
        """Errors column setter that stores an Exception and sets the ``valid`` flag."""
        self.valid = False
        self.collection = get_collection_from_marcxml(self.marcxml)
        self._errors = u'{}: {}'.format(type(value).__name__, value)

    @classmethod
    def from_marcxml(cls, raw_record):
        """Create an instance from a MARCXML record.

        The record must have a ``001`` tag containing the recid, otherwise it raises a ValueError.
        """
        try:
            recid = int(cls.re_recid.search(raw_record).group('recid'))
        except AttributeError:
            raise ValueError('The MARCXML record contains no recid or recid is malformed')
        # FIXME also get last_updated from marcxml
        record = cls(recid=recid)
        record.marcxml = raw_record
        record.valid = None
        return record


@db.event.listens_for(LegacyRecordsMirror, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    """Update `last_updated` property with current time on `before_update` event."""
    target.last_updated = datetime.utcnow()
