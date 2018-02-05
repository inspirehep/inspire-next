# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Multieditor utilities"""

from __future__ import absolute_import, print_function, division

from invenio_records.api import Record
from jsonschema import ValidationError
from inspire_schemas.api import validate

from inspirehep.utils.record import get_inspire_patch
from inspirehep.modules.migrator.tasks import chunker


def compare_records(old_records, new_records, schema):
    """Compares and validates the records after the actions have been applied
    :param old_records: records before actions
    :param new_records: records after actions
    :param schema: corresponding schema of the records
    Returns:
        json patches[object] and errors[string]
    """
    json_patches = []
    errors = []
    for index, new_record in enumerate(new_records):
        json_patches.append(get_inspire_patch(old_records[index], new_record))
        try:
            validate(new_record, schema)
        except ValidationError as e:
            errors.append(e.message)
        else:
            errors.append(None)
    return json_patches, errors


def match_records(records_ids, actions, schema):
        """Filter all results and return the affected number
        :param records_ids: ids of the records to be processed
        :param user_actions: user actions as received from frontend
        :param schema: corresponding schema of the records
        Returns:
            int: number of total matches
        """
        total_records_affected = 0
        for chunk in chunker(records_ids, 200):
            records = Record.get_records(chunk)
            for record in records:
                for action in actions:
                    action.process(record=record, schema=schema)
                    if action.changed:
                        total_records_affected += 1
                        action.changed = False
                        break
        return total_records_affected
