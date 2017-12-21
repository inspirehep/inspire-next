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


from __future__ import absolute_import, print_function, division

from celery import shared_task
from invenio_records.api import Record
from invenio_db import db

from inspirehep.modules.workflows.utils import with_debug_logging
from jsonschema import ValidationError
from .serializers import get_actions


@shared_task(ignore_result=True)
@with_debug_logging
def process_records(records_ids, user_actions, schema):
    """
    :param records_ids: ids of the records to be processed
    :param user_actions: user actions as received from frontend
    :param schema: corresponding schema for the records to be processed
    """
    commit_record = False
    commit_session = False
    errors = []
    actions = get_actions(user_actions, schema)
    records = Record.get_records(records_ids)
    for record in records:
        for action in actions:
            action.apply(record=record, schema=schema)
            if action.changed:
                commit_record = True
                action.changed = False
        if commit_record:
            try:
                record.commit()
            except (ValidationError, Exception) as e:
                errors.append(e.message)
            else:
                commit_session = True
            commit_record = False
    if commit_session:
        db.session.commit()
