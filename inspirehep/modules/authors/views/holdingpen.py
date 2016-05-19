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

"""INSPIRE authors holdingpen views."""

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)


from flask import abort, Blueprint, request, render_template
from flask_login import login_required

from invenio_db import db

from invenio_workflows import WorkflowObject, resume

blueprint = Blueprint('inspirehep_authors_holdingpen',
                      __name__,
                      url_prefix='/submit/author',
                      template_folder='../templates',
                      static_folder='../static')


@blueprint.route('/holdingpenreview', methods=['GET', 'POST'])
@login_required
# @permission_required(viewauthorreview.name)
def holdingpenreview():
    """Handler for approval or rejection of new authors in Holding Pen."""
    objectid = request.values.get('objectid', 0, type=int)
    approved = request.values.get('approved', False, type=bool)
    ticket = request.values.get('ticket', False, type=bool)
    if not objectid:
        abort(400)
    workflow_object = WorkflowObject.query.get(objectid)
    workflow_object.extra_data["approved"] = approved
    workflow_object.extra_data["ticket"] = ticket
    workflow_object.save()
    db.session.commit()

    resume.delay(workflow_object.id)

    return render_template('authors/forms/new_review_accepted.html',
                           approved=approved)
