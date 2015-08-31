# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Tasks related to record uploading."""

import jsonpatch

from invenio.ext.sqlalchemy import db
from invenio.ext.sqlalchemy.utils import session_manager

from invenio_records.api import create_record, get_record
from invenio_records.models import Record


def store_record_sip(obj, eng):
    """Update existing record via `control_number` or create new (SIP)."""
    from inspire.utils.helpers import get_model_from_obj
    model = get_model_from_obj(obj, eng)
    sip = model.get_latest_sip()
    record = sip.metadata
    if "control_number" in record:
        record['recid'] = record.get('control_number')
        create_related_record(record['recid'])
    _store_record(record)


def store_record(obj, eng):
    """Update existing record via `control_number` or create new (obj.data)."""
    record = obj.data
    if "control_number" in record:
        record['recid'] = record.get('control_number')
        create_related_record(record['recid'])
    _store_record(record)


@session_manager
def create_related_record(recid):
    """Create a record in BibRec as required when creating a new recid."""
    if Record.query.get(recid) is None:
        rec = Record(id=recid)
        db.session.add(rec)


@session_manager
def _store_record(record):
    """Update existing record via `control_number` or create new."""
    if "control_number" in record:
        existing_record = get_record(record['control_number'])
        if existing_record is not None:
            patch = jsonpatch.JsonPatch.from_diff(existing_record, record)
            updated_record = existing_record.patch(patch=patch)
            updated_record.commit()
        else:
            # New record with some hardcoded recid/control_number
            create_record(data=record)
    else:
        create_record(data=record)
