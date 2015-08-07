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

"""Blueprint for handling editing from Holding Pen."""

from invenio_deposit.helpers import make_record
from invenio_deposit.models import Deposition

from six import text_type
from flask import Blueprint, jsonify, request
from flask_login import login_required
from harvestingkit.html_utils import MathMLParser
from invenio.base.decorators import wash_arguments
from invenio.ext.principal import permission_required
from invenio_workflows.acl import viewholdingpen
from invenio_workflows.models import BibWorkflowObject


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
TITLE = "title"
URL = 'url'


@blueprint.route('/edit_record_title', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'value': (text_type, ""),
                 'objectid': (int, 0)})
def edit_record_title(value, objectid):
    """Entrypoint for editing title from detailed pages."""
    editable_obj = BibWorkflowObject.query.get(objectid)
    data = editable_obj.get_data()

    if type(data) is dict:
        deposition = Deposition(editable_obj)
        sip = deposition.get_latest_sip()
        metadata = sip.metadata

        metadata[TITLE][TITLE] = MathMLParser.html_to_text(value)
        sip.package = make_record(sip.metadata).legacy_export_as_marc()
        deposition.save()
    else:
        data[TITLE_FIELD] = MathMLParser.html_to_text(value)
        editable_obj.set_data(data)
        editable_obj.save()

    return jsonify({
        "category": "success",
        "message": "Edit on title was successful."
    })


@blueprint.route('/edit_record_urls', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'objectid': (text_type, "")})
def edit_record_urls(objectid):
    """Entrypoint for editing urls from detailed pages."""
    editable_obj = BibWorkflowObject.query.get(objectid)
    data = editable_obj.get_data()

    new_urls = request.values.getlist('urls[]') or []

    # We need to check the type of the object due to differences
    # Submission: dict /  Harvest: SmartJson
    if type(data) is dict:
        deposition = Deposition(editable_obj)
        sip = deposition.get_latest_sip()
        metadata = sip.metadata

        # Get the new urls and format them, the way the object does
        new_urls_array = []
        for url in new_urls:
            new_urls_array.append({'url': url})

        metadata[URL] = new_urls_array
        sip.package = make_record(sip.metadata).legacy_export_as_marc()
        deposition.save()
    else:
        # TODO: Does nothing, need to find how urls are structured
        pass

    return jsonify({
        "category": "success",
        "message": "Edit on urls was successful."
    })


@blueprint.route('/edit_record_subject', methods=['POST'])
@login_required
@permission_required(viewholdingpen.name)
@wash_arguments({'objectid': (text_type, "")})
def edit_record_subject(objectid):
    """Entrypoint for editing subjects from detailed pages."""
    editable_obj = BibWorkflowObject.query.get(objectid)
    data = editable_obj.get_data()

    new_subjects_list = request.values.getlist('subjects[]') or []
    subject_dict = []

    # We need to check the type of the object due to differences
    # Submission: dict /  Harvest: SmartJson
    if type(data) is dict:
        deposition = Deposition(editable_obj)
        sip = deposition.get_latest_sip()
        metadata = sip.metadata

        subject_dict.extend(metadata.get(SUBJECT_TERM))
        edit_submission(deposition, metadata, sip,
                        new_subjects_list, subject_dict)
    else:
        subject_dict.extend(data.get(SUBJECT_TERM))
        edit_harvest(editable_obj, data, new_subjects_list, subject_dict)

    return jsonify({
        "category": "success",
        "message": "Edit on subjects was successful."
    })


def edit_harvest(editable_obj, data, new_subjects_list, subject_dict):
    """Subject editing for harvested records."""
    old_subjects_list = data.get(SUBJECT_FIELD, [])

    data[SUBJECT_TERM] = revised_subjects_list(old_subjects_list,
                                               new_subjects_list,
                                               subject_dict)
    editable_obj.set_data(data)
    editable_obj.save()


def edit_submission(deposition, metadata, sip, new_subjects_list, subject_dict):
    """Subject editing for submissions."""
    old_subjects_list = []
    for subj in subject_dict:
        old_subjects_list.append(subj[TERM])

    metadata[SUBJECT_TERM] = revised_subjects_list(old_subjects_list,
                                                   new_subjects_list,
                                                   subject_dict)

    # hacky thing to update package as well, needed to show changes
    sip.package = make_record(sip.metadata).legacy_export_as_marc()
    deposition.save()


def revised_subjects_list(old, new, subject_dict):
    """Using sets, it determines which elements to remove
    and which to add when editing the subjects.
    """
    to_remove = [str(x) for x in list(set(old) - set(new))]
    to_add = [str(x) for x in list(set(new) - set(old))]

    # Remove subjects
    subject_objects = [subj for subj in subject_dict
                       if subj[TERM] not in to_remove]

    # Add the new subjects
    for subj in to_add:
        subject_objects.append({
            TERM: subj,
            SCHEME: INSPIRE_SCHEME
        })

    return subject_objects
