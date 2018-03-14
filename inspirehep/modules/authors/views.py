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

"""INSPIRE authors views."""

from __future__ import absolute_import, division, print_function

import copy
import requests

from flask import (
    abort,
    Blueprint,
    jsonify,
    render_template,
    request,
    url_for,
)
from flask_breadcrumbs import register_breadcrumb
from flask_login import login_required, current_user
from inspire_utils.record import get_value
from invenio_db import db
from invenio_workflows import workflow_object_class, start, resume
from invenio_workflows_ui.api import WorkflowUIRecord
from werkzeug.datastructures import MultiDict

from inspirehep.modules.forms.form import DataExporter
from inspirehep.utils.record_getter import RecordGetterError, get_db_record
from inspirehep.utils.url import get_legacy_url_for_recid
from .forms import AuthorUpdateForm
from .permissions import holdingpen_author_permission
from .tasks import formdata_to_model
from .core import convert_for_form
from .utils import get_author_record_from_xml_response

blueprint = Blueprint(
    'inspirehep_authors',
    __name__,
    url_prefix='/authors',
    template_folder='templates',
    static_folder='static',
)


def get_inspire_url(data):
    """ Generate url for the user to go back to INSPIRE. """
    url = ""
    if "bai" in data and data["bai"]:
        url = "http://inspirehep.net/author/profile/" + data["bai"]
    elif "control_number" in data and data["control_number"]:
        url = "http://inspirehep.net/record/" + str(data["control_number"])
    else:
        url = "http://inspirehep.net/hepnames"
    return url


@blueprint.route('/validate', methods=['POST'])
def validate():
    """Validate form and return validation errors.

    FIXME: move to forms module as a generic /validate where we can pass
    the for class to validate.
    """
    if request.method != 'POST':
        abort(400)

    is_update = True if request.args.get('is_update') == 'True' else False
    data = request.json or MultiDict({})
    formdata = MultiDict(data or {})
    form = AuthorUpdateForm(formdata=formdata, is_update=is_update)
    form.validate()

    result = {}
    changed_msgs = dict(
        (name, messages) for name, messages in form.messages.items()
        if name in formdata.keys()
    )
    result['messages'] = changed_msgs

    return jsonify(result)


@blueprint.route('/new', methods=['GET'])
@register_breadcrumb(blueprint, '.new', 'New author information')
@login_required
def new():
    """View for INSPIRE author new form."""
    data = {}
    bai = request.values.get('bai', u"", type=unicode)
    if bai:
        # Add BAI information to form in order to keep connection between
        # a HEPName and an author profile.
        data["bai"] = bai

    form = AuthorUpdateForm(data=data)

    ctx = {
        "action": url_for('.submitnew'),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
    }

    return render_template('authors/forms/new_form.html', form=form, **ctx)


@blueprint.route('/<int:recid>/update', methods=['GET'])
@register_breadcrumb(blueprint, '.update', 'Update author information')
@login_required
def update(recid):
    """View for INSPIRE author update form."""
    try:
        data = get_db_record('aut', recid)
    except RecordGetterError:
        # TODO: a different approach will be needed when Legacy shuts down.
        try:
            url = get_legacy_url_for_recid(recid) + '/export/xm'
            xml_response = requests.get(url)
            xml_response.raise_for_status()
        except requests.exceptions.RequestException:
            if xml_response.status_code == 404:
                abort(404)
            abort(400)

        data = get_author_record_from_xml_response(xml_response.content)

    if not data:
        abort(400)

    convert_for_form(data)
    data['control_number'] = recid

    form = AuthorUpdateForm(data=data, is_update=True)
    ctx = {
        "action": url_for('.submitupdate'),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
    }

    return render_template('authors/forms/update_form.html', form=form, **ctx)


@blueprint.route('/update/submit', methods=['POST'])
@login_required
def submitupdate():
    """Form action handler for INSPIRE author update form."""
    form = AuthorUpdateForm(formdata=request.form, is_update=True)
    visitor = DataExporter()
    visitor.visit(form)

    workflow_object = workflow_object_class.create(
        data={},
        id_user=current_user.get_id(),
        data_type="authors"
    )

    workflow_object.extra_data['formdata'] = copy.deepcopy(visitor.data)
    workflow_object.extra_data['is-update'] = True
    workflow_object.data = formdata_to_model(workflow_object, visitor.data)
    workflow_object.save()
    db.session.commit()

    # Start workflow. delay will execute the workflow in the background
    start.delay("author", object_id=workflow_object.id)

    ctx = {
        "inspire_url": get_inspire_url(visitor.data)
    }

    return render_template('authors/forms/update_success.html', **ctx)


@blueprint.route('/new/submit', methods=['POST'])
@login_required
def submitnew():
    """Form action handler for INSPIRE author new form."""
    form = AuthorUpdateForm(formdata=request.form)
    visitor = DataExporter()
    visitor.visit(form)

    workflow_object = workflow_object_class.create(
        data={},
        id_user=current_user.get_id(),
        data_type="authors"
    )
    workflow_object.extra_data['formdata'] = copy.deepcopy(visitor.data)
    workflow_object.extra_data['is-update'] = False
    workflow_object.data = formdata_to_model(workflow_object, visitor.data)
    workflow_object.save()
    db.session.commit()

    # Start workflow. delayed=True will execute the workflow in the
    # background using, for example, Celery.
    start.delay("author", object_id=workflow_object.id)

    ctx = {
        "inspire_url": get_inspire_url(visitor.data)
    }

    return render_template('authors/forms/new_success.html', **ctx)


@blueprint.route('/new/review', methods=['GET'])
@login_required
@holdingpen_author_permission.require(http_exception=403)
def newreview():
    """View for INSPIRE author new form review by a cataloger."""
    objectid = request.values.get('objectid', 0, type=int)
    if not objectid:
        abort(400)

    workflow_metadata = WorkflowUIRecord.get_record(objectid)['metadata']

    # Converting json to populate form
    workflow_metadata['extra_comments'] = get_value(
        workflow_metadata,
        '_private_notes[0].value'
    )
    convert_for_form(workflow_metadata)

    form = AuthorUpdateForm(
        data=workflow_metadata, is_review=True)
    ctx = {
        "action": url_for('.reviewhandler', objectid=objectid),
        "name": "authorUpdateForm",
        "id": "authorUpdateForm",
        "objectid": objectid
    }

    return render_template('authors/forms/review_form.html', form=form, **ctx)


@blueprint.route('/new/review/submit', methods=['POST'])
@login_required
@holdingpen_author_permission.require(http_exception=403)
def reviewhandler():
    """Form handler when a cataloger accepts an author review."""
    objectid = request.values.get('objectid', 0, type=int)
    if not objectid:
        abort(400)

    form = AuthorUpdateForm(formdata=request.form)
    visitor = DataExporter()
    visitor.visit(form)

    workflow_object = workflow_object_class.get(objectid)
    workflow_object.extra_data["approved"] = True
    workflow_object.extra_data["ticket"] = request.form.get('ticket') == "True"
    workflow_object.extra_data['formdata'] = visitor.data
    workflow_object.data = formdata_to_model(workflow_object, visitor.data)
    workflow_object.save()
    db.session.commit()

    resume.delay(workflow_object.id)

    return render_template('authors/forms/new_review_accepted.html',
                           approved=True)


@blueprint.route('/holdingpenreview', methods=['GET', 'POST'])
@login_required
@holdingpen_author_permission.require(http_exception=403)
def holdingpenreview():
    """Handler for approval or rejection of new authors in Holding Pen."""
    objectid = request.values.get('objectid', 0, type=int)
    approved = request.values.get('approved', False, type=bool)
    ticket = request.values.get('ticket', False, type=bool)
    if not objectid:
        abort(400)
    workflow_object = workflow_object_class.get(objectid)
    workflow_object.extra_data["approved"] = approved
    workflow_object.extra_data["ticket"] = ticket
    workflow_object.extra_data['is-update'] = False
    workflow_object.save()
    db.session.commit()

    resume.delay(workflow_object.id)

    return render_template('authors/forms/new_review_accepted.html',
                           approved=approved)
