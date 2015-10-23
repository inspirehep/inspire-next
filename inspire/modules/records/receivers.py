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

from invenio.ext.sqlalchemy import db

from invenio_records.models import Record

from invenio_records.signals import before_record_insert


@before_record_insert.connect
def insert_record(sender, *args, **kwargs):
    """Hack record insertion to add unregistered records.

    This handler is imported when --force flag is used.
    Example: inveniomanage migrator populate -f inspire/demosite/data/demo-records.xml --force
    """
    if 'control_number' in sender:
        control_number = sender['control_number']
        control_number = int(control_number)
        # Searches if record already exists.
        record = Record.query.filter_by(id=control_number).first()
        if record is None:
            # Adds the record to the db.
            rec = Record(id=control_number)
            db.session.add(rec)


def remove_handler():
    """Disconnects the signal handler."""
    before_record_insert.disconnect(insert_record)
