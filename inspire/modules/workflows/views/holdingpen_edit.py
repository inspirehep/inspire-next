# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# 59 Tseemple Place, Suite 330, Boston, MA 02111-1307, USA.

from six import text_type
from flask import Blueprint, jsonify, request
from flask_login import login_required
from harvestingkit.html_utils import MathMLParser
from invenio.base.decorators import wash_arguments
from invenio.ext.principal import permission_required
from invenio.modules.workflows.acl import viewholdingpen
from invenio.modules.workflows.models import BibWorkflowObject


blueprint = Blueprint(
    'inspire_holdingpen',
    __name__,
    url_prefix="/admin/holdingpen",
    template_folder='../templates',
    static_folder="../static",
)


# Constants
SUBJECT_TERM = "subject_term"
TERM = "term"
SCHEME = "scheme"
INSPIRE_SCHEME = "INSPIRE"

# Fields
SUBJECT_FIELD = "subject_term.term"
TITLE_FIELD = "title.title"


@blueprint.route('/edit_record_title', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'value': (text_type, ""),
                 'objectid': (int, 0)})
def edit_record_title(value, objectid):
    """Entrypoint for editing title from detailed pages."""
    editable_obj = BibWorkflowObject.query.get(objectid)
    data = editable_obj.get_data()

    data[TITLE_FIELD] = MathMLParser.html_to_text(value)
    editable_obj.set_data(data)
    editable_obj.save()

    return jsonify({
        "category": "success",
        "message": "Edit on title was successful"
    })


@blueprint.route('/edit_record_subject', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'objectid': (text_type, "")})
def edit_record_subject(objectid):
    """Entrypoint for editing subjects from detailed pages."""
    editable_obj = BibWorkflowObject.query.get(objectid)
    data = editable_obj.get_data()

    old_subjects_list = data.get(SUBJECT_FIELD, [])
    new_subjects_list = request.values.getlist('subjects[]') or []

    # We will use a diff method to find which
    # subjects to remove and which to add.
    # PLUS removes unicode
    to_remove = [str(x) for x in list(set(old_subjects_list) - set(new_subjects_list))]
    to_add = [str(x) for x in list(set(new_subjects_list) - set(old_subjects_list))]

    # Make a copy of the original list
    subject_objects = []
    subject_objects.extend(data.get(SUBJECT_TERM, []))

    # Remove subjects
    subject_objects = [subj for subj in subject_objects
                       if subj[TERM] not in to_remove]

    # Add the new subjects
    for subj in to_add:
        subject_objects.append({
            TERM: subj,
            SCHEME: INSPIRE_SCHEME
        })

    data[SUBJECT_TERM] = subject_objects
    editable_obj.set_data(data)
    editable_obj.save()

    return jsonify({
        "category": "success",
        "message": "Edit on subjects was successful"
    })
