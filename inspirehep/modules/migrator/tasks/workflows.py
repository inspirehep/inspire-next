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


@shared_task()
def import_holdingpen_record(obj, eng):
    """Import an hp record."""
    from invenio_db import db
    from workflow.engine_db import WorkflowStatus
    from invenio_workflows import (
        Workflow, WorkflowObject, ObjectStatus
    )
    engine_model = Workflow(
        name=eng['name'],
        created=iso8601.parse_date(eng['created']),
        modified=iso8601.parse_date(eng['modified']),
        id_user=eng['id_user'],
        status=WorkflowStatus(eng['status']),
        uuid=eng['uuid'],
    )
    engine_model.extra_data = eng['extra_data']

    object_model = WorkflowObject(
        id=obj['id'],
        created=iso8601.parse_date(eng['created']),
        modified=iso8601.parse_date(eng['modified']),
        data_type=obj['data_type'],
        id_user=obj['id_user'],
        id_workflow=obj['id_workflow'],
        id_parent=obj['id_parent'],
        status=ObjectStatus(obj['status']),
        callback_pos=obj['extra_data']['_task_counter'],
    )
    # Data adjustments
    # ================
    if eng['name'] in ['process_record_arxiv', 'literature']:
        # We need to convert a few things..
        # subject_terms -> field_categories
        obj['data']['field_categories'] = obj['data'].pop('subject_terms', [])

        # change urls.url to urls.value
        obj['data']['urls'] = [
            dict(value=u.pop('url', None), **u)
            for u in obj['data'].get('urls', [])
        ]

    object_model.data = obj['data']

    # Extra data adjustments
    # ======================
    # Re-place classifier extraction data
    old_classifier = obj['extra_data']['_tasks_results'].get('classification')
    if old_classifier:
        obj['extra_data']['classifier_results'] = old_classifier[0]['result']

    # Re-place prediction data extraction data
    old_relevance = obj['extra_data']['_tasks_results'].get('arxiv_guessing')
    if old_relevance:
        old_relevance = old_relevance[0]['result']
        obj['extra_data']['relevance_prediction'] = dict(
            max_score=old_relevance['max_score'],
            decision=old_relevance['decision'],
            relevance_score=old_relevance['relevance_score'],
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

    db.session.add(engine_model)
    db.session.add(object_model)
    db.session.commit()
