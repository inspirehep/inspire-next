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
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Blueprint for handling editing from Holding Pen."""

from invenio_deposit.helpers import make_record

from six import text_type
from flask import Blueprint, jsonify, request
from flask_login import login_required
from harvestingkit.html_utils import MathMLParser
from invenio.base.decorators import wash_arguments
from invenio.ext.principal import permission_required
from invenio_workflows.acl import viewholdingpen
from invenio_workflows.models import BibWorkflowObject
from inspire.utils.helpers import get_model_from_obj


blueprint = Blueprint(
    'inspire_holdingpen',
    __name__,
    url_prefix="/admin/holdingpen",
    template_folder='../templates',
    static_folder="../static",
)


# Constants
SUBJECT_TERM = "subject_term"
VALUE = "value"
SCHEME = "scheme"
INSPIRE_SCHEME = "INSPIRE"

# Fields
SUBJECT_FIELD = "subject_term.term"
TITLE_FIELD = "title.title"
TITLE = "title"
URL = 'url'


# Helper methods for editing
def get_attributes(objectid):
    """Returns the required attributes for record editing."""
    editable_obj = BibWorkflowObject.query.get(objectid)
    model = get_model_from_obj(editable_obj)
    sip = model.get_latest_sip()
    metadata = sip.metadata

    return model, sip, metadata


def save_changes(sip, model):
    """Saves the changes in the record."""
    sip.package = make_record(sip.metadata)
    model.save()


def json_success_message(attribute):
    return jsonify({
        "category": "success",
        "message": "Edit on {0} was successful.".format(attribute)
    })


@blueprint.route('/edit_record_title', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'value': (text_type, ""),
                 'objectid': (int, 0)})
def edit_record_title(value, objectid):
    """Entrypoint for editing title from detailed pages."""
    model, sip, metadata = get_attributes(objectid)

    metadata[TITLE][TITLE] = MathMLParser.html_to_text(value)
    save_changes(sip, model)
    return json_success_message('title')


@blueprint.route('/edit_record_urls', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'objectid': (text_type, "")})
def edit_record_urls(objectid):
    """Entrypoint for editing urls from detailed pages."""
    model, sip, metadata = get_attributes(objectid)
    new_urls = request.values.getlist('urls[]') or []

    # Get the new urls and format them, the way the object does
    new_urls_array = []
    for url in new_urls:
        new_urls_array.append({'url': url})

    metadata[URL] = new_urls_array
    save_changes(sip, model)
    return json_success_message('urls')


@blueprint.route('/edit_record_subject', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'objectid': (text_type, "")})
def edit_record_subject(objectid):
    """Entrypoint for editing subjects from detailed pages."""
    model, sip, metadata = get_attributes(objectid)
    new_subjects_list = request.values.getlist('subjects[]') or []

    subject_dict = []
    subject_dict.extend(metadata.get(SUBJECT_TERM))

    old_subjects_list = []
    for subj in subject_dict:
        old_subjects_list.append(subj[VALUE])

    metadata[SUBJECT_TERM] = revised_subjects_list(old_subjects_list,
                                                   new_subjects_list,
                                                   subject_dict)
    save_changes(sip, model)
    return json_success_message('subjects')


def revised_subjects_list(old, new, subject_dict):
    """Using sets, it determines which elements to remove
    and which to add when editing the subjects.
    """
    to_remove = [str(x) for x in list(set(old) - set(new))]
    to_add = [str(x) for x in list(set(new) - set(old))]

    # Remove subjects
    subject_objects = [subj for subj in subject_dict
                       if subj[VALUE] not in to_remove]

    # Add the new subjects
    for subj in to_add:
        subject_objects.append({
            VALUE: subj,
            SCHEME: INSPIRE_SCHEME
        })

    return subject_objects
