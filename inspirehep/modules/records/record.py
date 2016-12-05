# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Inspire Record inherits from Invenio Record"""

from __future__ import absolute_import, division, print_function

from invenio_records.api import Record

from inspirehep.dojson.utils import get_recid_from_url
from inspirehep.utils.helpers import get_pid_type_from_ref
from inspirehep.utils.record import (
    get_value,
    merge_pidstores_of_two_merged_records,
    soft_delete_pidstore_for_record,
)
from inspirehep.utils.record_getter import get_db_record


class InspireRecord(Record):

    """Inspire Record inherits from Invenio Record."""

    def __init__(self, data=None, model=None):
        super(InspireRecord, self).__init__(data=data, model=model)

    def merge(self, new):
        def _get_merge_db_record(new_reference):
            new_recid = get_recid_from_url(new_reference)
            pid_type = get_pid_type_from_ref(new_reference)

            return get_db_record(pid_type, new_recid)

        # Before record update
        new_record = _get_merge_db_record(new)
        merge_pidstores_of_two_merged_records(new_record.id, self.id)

        self['deleted'] = True
        self['new_record'] = {'$ref': new}
        self.commit()

        # After record update
        from inspirehep.modules.records.tasks import update_refs

        old = get_value(self, 'self.$ref')
        update_refs.delay(old, new)

    def delete(self, force=False):
        if force:
            super(InspireRecord, self).delete(force=True)
        else:
            self['deleted'] = True
            soft_delete_pidstore_for_record(self.id)
            self.commit()
