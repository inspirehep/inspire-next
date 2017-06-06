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

"""Models for relations."""

from datetime import datetime
from zlib import compress, decompress, error

from invenio_db import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types import JSONType, UUIDType


class Relations(db.Model):
    __tablename__ = 'relations'

    from_id = db.Column(
        UUIDType,
        db.ForeignKey('records_metadata.id'),
        index=True,
        nullable=False,

    )
    from_type = db.Column(db.String(length=255), index=True, nullable=False),
    to_id = db.Column(
        UUIDType,
        db.ForeignKey('records_metadata.id'),
        index=True,
        nullable=False
    )
    to_type = db.Column(db.String(length=255), index=True, nullable=False),
    relation = db.Column(db.String(length=255), index=True, nullable=False)
    path = db.Column(db.String(length=255), index=True, nullable=False)
