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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Model of the database table."""

from __future__ import absolute_import, division, print_function

from datetime import datetime

from invenio_db import db


class DisambiguationRecord(db.Model):
    """Model of the table to keep track of publications to be clustered."""
    __tablename__ = "disambiguation_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    record_id = db.Column(db.String(length=36), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def save(self):
        """Create an object, which later will be stored in the database."""
        with db.session.begin_nested():
            db.session.add(self)
