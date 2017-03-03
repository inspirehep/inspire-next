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

from datetime import datetime
from zlib import compress, decompress, error

from invenio_db import db
from sqlalchemy.ext.hybrid import hybrid_property


class InspireProdRecords(db.Model):
    __tablename__ = 'inspire_prod_records'

    recid = db.Column(db.Integer, primary_key=True, index=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    _marcxml = db.Column('marcxml', db.LargeBinary, nullable=False)
    valid = db.Column(db.Boolean, default=None, nullable=True, index=True)
    errors = db.Column(db.Text(), nullable=True)

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
