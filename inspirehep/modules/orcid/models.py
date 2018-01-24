# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""Models for ORCID integration."""

from __future__ import absolute_import, division, print_function

from invenio_db import db


class InspireOrcidPutCodes(db.Model):
    __tablename__ = 'inspire_orcid_put_codes'

    recid = db.Column(db.Integer, primary_key=True, index=True)
    put_code = db.Column(db.Integer, nullable=False, index=True)

    @classmethod
    def set_put_code(cls, recid, put_code):
        """Set a put-code for a record.

        Args:
            recid (int): record ID
            put_code (int): ORCID put-code
        """
        query_existing = cls.query.filter_by(recid=recid)
        if query_existing.count() >= 1:
            query_existing.one().put_code = put_code
            return

        entry = cls()
        entry.recid = recid
        entry.put_code = put_code
        with db.session.begin_nested():
            db.session.add(entry)

    @classmethod
    def get_put_code(cls, recid):
        """Get put-code for a record.

        Args:
            recid (int): record ID

        Returns:
            Union[int, None]: put-code for record, or None if not set
        """
        query = cls.query.filter_by(recid=recid)
        if query.count() >= 1:
            return query.one().put_code
