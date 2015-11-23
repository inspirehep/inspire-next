# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

"""Models for Migrator."""

from datetime import datetime

from invenio_ext.sqlalchemy import db


class InspireProdRecords(db.Model):
    __tablename__ = 'inspire_prod_records'

    recid = db.Column(db.Integer, primary_key=True, index=True)
    last_updated = db.Column(db.DateTime, default=datetime.now, nullable=False)
    marcxml = db.Column(db.LargeBinary, nullable=False)
    successful = db.Column(db.Boolean, default=None, nullable=True)
