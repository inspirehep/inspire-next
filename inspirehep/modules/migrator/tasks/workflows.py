# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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


"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

import iso8601

from celery import shared_task
from sqlalchemy.exc import IntegrityError

from inspirehep.modules.authors.tasks import formdata_to_model


DATA_TYPE_MAP = {
    "Author New": "authors",
    "Author Update": "authors",
    "submission": "hep"
}

WORKFLOW_NAME_MAP = {
    "authornew": "author",
    "authorupdate": "author",
    "literature": "article"
}


def fix_object_model(eng, obj):
    # Data adjustments
    # ================
    if eng['name'] in ('authornew', 'authorupdate'):
        obj.data = formdata_to_model(obj, obj.extra_data.get('formdata'))

        if eng['name'] == 'authorupdate':
            obj.extra_data['is-update'] = True
        else:
            obj.extra_data['is-update'] = False

    if eng['name'] in ['process_record_arxiv', 'literature']:
        # We need to convert a few things..
        # subject_terms -> field_categories
        obj.data['field_categories'] = obj.data.pop('subject_terms', [])

        # change urls.url to urls.value
        obj.data['urls'] = [
            dict(value=u.pop('url', None), **u)
            for u in obj.data.get('urls', [])
        ]

    # Extra data adjustments
    # ======================
    # Re-place classifier extraction data
    old_classifier = obj.extra_data['_tasks_results'].get('classification')
    if old_classifier:
        obj.extra_data['classifier_results'] = old_classifier[0]['result']

    # Re-place prediction data extraction data
    old_relevance = obj.extra_data['_tasks_results'].get('arxiv_guessing')
    if old_relevance:
        old_relevance = old_relevance[0]['result']
        obj.extra_data['relevance_prediction'] = dict(
            max_score=old_relevance['max_score'],
            decision=old_relevance['decision'],
            relevance_score=old_relevance.get('relevance_score'),
            scores={
                'CORE': old_relevance['all_scores'][0],
                'Non-CORE': old_relevance['all_scores'][1],
                'Rejected': old_relevance['all_scores'][2],
            },
            top_words={
                'CORE': old_relevance.get('top_core', []),
                'Non-CORE': old_relevance.get('top_noncore', []),
                'Rejected': old_relevance.get('top_rejected', []),
            },
        )


@shared_task()
def import_holdingpen_record(parent_objs, obj, eng):
    """Import an hp record."""
    from invenio_db import db
    from workflow.engine_db import WorkflowStatus
    from invenio_workflows import (
        Workflow, WorkflowObject, ObjectStatus
    )
    engine_model = Workflow(
        name=WORKFLOW_NAME_MAP.get(eng['name'], eng['name']),
        created=iso8601.parse_date(eng['created']),
        modified=iso8601.parse_date(eng['modified']),
        id_user=eng['id_user'],
        status=WorkflowStatus(eng['status']),
        uuid=eng['uuid'],
    )
    engine_model.extra_data = eng['extra_data']

    db.session.add(engine_model)
    try:
        db.session.commit()
    except IntegrityError:
        # The model has already been added to the DB.
        db.session.rollback()

    # First create parents
    if parent_objs:
        for parent in parent_objs:
            object_model = WorkflowObject.create(
                {},  # Pass empty data (filled later)
                id=parent['id'],
                created=iso8601.parse_date(eng['created']),
                modified=iso8601.parse_date(eng['modified']),
                data_type=DATA_TYPE_MAP.get(parent['data_type'], parent['data_type']),
                id_user=parent['id_user'],
                id_workflow=parent['id_workflow'],
                id_parent=parent['id_parent'],
                status=ObjectStatus(parent['status']),
                callback_pos=parent['extra_data']['_task_counter'],
            )

            object_model.data = obj['data']
            object_model.extra_data = obj['extra_data']
            fix_object_model(eng, object_model)
            object_model.save()

    # And then the object
    object_model = WorkflowObject.create(
        {},  # Pass empty data (filled later)
        id=obj['id'],
        created=iso8601.parse_date(eng['created']),
        modified=iso8601.parse_date(eng['modified']),
        data_type=DATA_TYPE_MAP.get(obj['data_type'], obj['data_type']),
        id_user=obj['id_user'],
        id_workflow=obj['id_workflow'],
        id_parent=obj['id_parent'],
        status=ObjectStatus(obj['status']),
        callback_pos=obj['extra_data']['_task_counter'],
    )

    object_model.data = obj['data']
    object_model.extra_data = obj['extra_data']
    fix_object_model(eng, object_model)
    object_model.save()

    db.session.commit()
