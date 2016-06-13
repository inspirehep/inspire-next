# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

"""INSPIRE Literature suggestion blueprint."""

from __future__ import absolute_import, print_function

import copy

from flask import (
    abort,
    Blueprint,
    redirect,
    request,
    render_template,
    url_for,
    jsonify,
)
from flask_login import current_user, login_required

from werkzeug.datastructures import MultiDict

from inspirehep.modules.forms.form import DataExporter

from invenio_db import db
from invenio_workflows import WorkflowObject, start

from .forms import LiteratureForm
from .tasks import formdata_to_model


blueprint = Blueprint('inspirehep_literature_suggest',
                      __name__,
                      url_prefix='/submit/literature',
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('/create', methods=['GET'])
@login_required
def create():
    """View for INSPIRE suggestion create form."""
    form = LiteratureForm()
    ctx = {
        "action": url_for('.submit'),
        "name": "submitForm",
        "id": "submitForm",
    }

    return render_template(
        'literaturesuggest/forms/suggest.html',
        form=form,
        **ctx
    )


@blueprint.route('/create/submit', methods=['POST'])
def submit():
    """Get form data and start workflow."""
    form = LiteratureForm(formdata=request.form)
    visitor = DataExporter()
    visitor.visit(form)

    workflow_object = WorkflowObject.create_object(
        id_user=current_user.get_id())
    workflow_object.data_type = "hep"
    workflow_object.extra_data['formdata'] = copy.deepcopy(visitor.data)
    workflow_object.data = formdata_to_model(workflow_object, visitor.data)
    workflow_object.save()
    db.session.commit()

    # Start workflow. delayed=True will execute the workflow in the
    # background using, for example, Celery.
    start.delay("article", object_id=workflow_object.id)

    return redirect(url_for('.success'))


@blueprint.route('/create/success', methods=['GET'])
def success():
    """Render success template for the user."""
    return render_template('literaturesuggest/forms/suggest_success.html')


@blueprint.route('/validate', methods=['POST'])
def validate():
    """Validate form and return validation errors.

    FIXME: move to forms module as a generic /validate where we can pass
    the for class to validate.
    """
    if request.method != 'POST':
        abort(400)
    data = request.json or MultiDict({})
    formdata = MultiDict(data or {})
    form = LiteratureForm(formdata=formdata)
    form.validate()

    result = {}
    changed_msgs = dict(
        (name, messages) for name, messages in form.messages.items()
        if name in formdata.keys()
    )
    result['messages'] = changed_msgs

    return jsonify(result)
