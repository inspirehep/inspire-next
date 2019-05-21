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

from __future__ import absolute_import, division, print_function

from flask import current_app
from sqlalchemy_continuum import transaction_class

from invenio_db import db
from invenio_records.models import RecordMetadata

from inspirehep.modules.workflows.tasks.actions import validate_record
from inspirehep.modules.workflows.tasks.submission import cleanup_pending_workflow, send_robotupload
from inspirehep.modules.workflows.tasks.upload import send_record_to_hep
from inspirehep.modules.workflows.utils import get_resolve_edit_article_callback_url
from inspirehep.utils.record_getter import get_db_record
from ..utils import with_debug_logging


@with_debug_logging
def change_status_to_waiting(obj, eng):
    obj.extra_data['callback_url'] = get_resolve_edit_article_callback_url()
    eng.wait(msg='Waiting for curation.')


def update_record(obj, eng):
    control_number = obj.data['control_number']
    if current_app.config.get("FEATURE_FLAG_ENABLE_REST_RECORD_MANAGEMENT"):
        endpoint = '/literature'
        send_record_to_hep(obj, endpoint, control_number)
    else:
        record = get_db_record('lit', control_number)
        record.update(obj.data)
        record.commit()

        user_id = obj.id_user
        if user_id:
            _set_transaction_user_id_for_last_record_update(control_number, user_id)

        db.session.commit()


def _set_transaction_user_id_for_last_record_update(control_number, user_id):
    record = get_db_record('lit', control_number)
    revision = record.model.versions.filter_by(version_id=(record.revision_id + 1)).one()
    transaction_id = revision.transaction_id

    Transaction = transaction_class(RecordMetadata)
    transaction = Transaction.query.filter(Transaction.id == transaction_id).one()
    transaction.user_id = user_id

    db.session.add(transaction)


class EditArticle(object):
    """Editing workflow for Literature collection."""

    name = 'edit_article'
    data_type = 'hep'

    workflow = (
        [
            change_status_to_waiting,
            validate_record('hep'),
            update_record,
            send_robotupload(mode='replace', priority_config_key='LEGACY_ROBOTUPLOAD_PRIORITY_EDIT_ARTICLE'),
            cleanup_pending_workflow,
        ]
    )
