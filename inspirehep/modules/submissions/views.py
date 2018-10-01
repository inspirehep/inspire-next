# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

"""Submissions views."""

from __future__ import absolute_import, division, print_function

import copy
import datetime
import json

from sqlalchemy.orm.exc import NoResultFound

from flask import Blueprint, abort, jsonify, request
from flask.views import MethodView
from flask_login import current_user

from invenio_db import db
from invenio_workflows import workflow_object_class, start
from invenio_oauthclient.models import UserIdentity

from .serializers.json import author_serializer
from .utils import get_record_from_legacy

blueprint = Blueprint(
    'inspirehep_submissions',
    __name__,
    template_folder='templates',
    url_prefix='/submissions',
)


class SubmissionsResource(MethodView):

    endpoint_to_data_type = {
        'literature': 'hep',
        'authors': 'authors',
    }

    endpoint_to_workflow_name = {
        'literature': 'article',
        'authors': 'author',
    }

    endpoint_to_form_serializer = {
        'authors': author_serializer,
    }

    def get(self, endpoint, pid_value=None):
        record = get_record_from_legacy(pid_value)
        if not record:
            abort(404)

        serializer = self._get_serializer_from_endpoint(endpoint)
        serialized_record = serializer().dump(record)
        return jsonify({'data': serialized_record.data})

    def post(self, endpoint):
        submission_data = json.loads(request.data)
        workflow_object_id = self.start_workflow_for_submission(
            endpoint, submission_data['data'])
        return jsonify({'workflow_object_id': workflow_object_id})

    def put(self, endpoint, pid_value):
        submission_data = json.loads(request.data)
        workflow_object_id = self.start_workflow_for_submission(
            endpoint, submission_data['data'], pid_value)
        return jsonify({'workflow_object_id': workflow_object_id})

    def start_workflow_for_submission(self, endpoint, submission_data,
                                      control_number=None):
        workflow_object = workflow_object_class.create(
            data={},
            id_user=current_user.get_id(),
            data_type=self.endpoint_to_data_type[endpoint]
        )

        submission_data['acquisition_source'] = dict(
            email=current_user.email,
            datetime=datetime.datetime.utcnow().isoformat(),
            method='submitter',
            submission_number=str(workflow_object.id),
            internal_uid=int(workflow_object.id_user),
        )

        orcid = self._get_user_orcid()
        if orcid:
            submission_data['acquisition_source']['orcid'] = orcid

        serializer = self._get_serializer_from_endpoint(endpoint)
        serialized_data = serializer().load(submission_data).data

        if control_number:
            serialized_data['control_number'] = int(control_number)

        workflow_object.data = serialized_data
        workflow_object.extra_data['is-update'] = bool(control_number)

        workflow_object.extra_data['source_data'] = {
            'data': copy.deepcopy(workflow_object.data),
            'extra_data': copy.deepcopy(workflow_object.extra_data)
        }

        workflow_object.save()
        db.session.commit()

        workflow_object_id = workflow_object.id

        start.delay(
            self.endpoint_to_workflow_name[endpoint], object_id=workflow_object.id)

        return workflow_object_id

    def _get_user_orcid(self):
        try:
            orcid = UserIdentity.query.filter_by(
                id_user=current_user.get_id(),
                method='orcid'
            ).one().id
            return orcid
        except NoResultFound:
            return None

    def _get_serializer_from_endpoint(self, endpoint):
        if endpoint not in self.endpoint_to_form_serializer:
            abort(400)
        return self.endpoint_to_form_serializer[endpoint]


submissions_view = SubmissionsResource.as_view(
    'submissions_view'
)

blueprint.add_url_rule(
    '/<endpoint>',
    view_func=submissions_view,
)
blueprint.add_url_rule(
    '/<endpoint>/<int:pid_value>',
    view_func=submissions_view,
)
