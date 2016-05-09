# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

from six import text_type

from flask import Blueprint, jsonify, request
from flask_login import login_required

from harvestingkit.html_utils import MathMLParser

# from invenio_ext.principal import permission_required
from invenio_db import db
# from invenio_workflows.acl import viewholdingpen
from invenio_workflows import WorkflowObject


blueprint = Blueprint(
    'inspire_holdingpen',
    __name__,
    url_prefix="/holdingpen",
    template_folder='../templates',
    static_folder="../static",
)


def json_success_message(attribute):
    return jsonify({
        "category": "success",
        "message": "Edit on {0} was successful.".format(attribute)
    })


@blueprint.route('/edit_record_title', methods=['POST'])
@login_required
# @permission_required(viewholdingpen.name)
def edit_record_title():
    """Entrypoint for editing title from detailed pages."""
    value = request.values.get('value', '', type=text_type)
    objectid = request.values.get('objectid', 0, type=int)
    obj = WorkflowObject.query.get(objectid)
    obj.data["titles"][0] = {"title": MathMLParser.html_to_text(value)}
    obj.save()
    db.session.commit()
    return json_success_message('title')


@blueprint.route('/edit_record_urls', methods=['POST'])
@login_required
# @permission_required(viewholdingpen.name)
def edit_record_urls():
    """Entrypoint for editing urls from detailed pages."""
    objectid = request.values.get('objectid', 0, type=int)
    new_urls = request.values.getlist('urls[]') or []

    obj = WorkflowObject.query.get(objectid)

    # Get the new urls and format them, the way the object does
    new_urls_array = []
    for url in new_urls:
        new_urls_array.append({'url': url})

    obj.data['urls'] = new_urls_array
    obj.save()
    db.session.commit()
    return json_success_message('urls')


@blueprint.route('/edit_record_subject', methods=['POST'])
@login_required
# @permission_required(viewholdingpen.name)
def edit_record_subject():
    """Entrypoint for editing subjects from detailed pages."""
    objectid = request.values.get('objectid', 0, type=int)
    new_subjects_list = request.values.getlist('subjects[]') or []

    obj = WorkflowObject.query.get(objectid)

    subject_dict = []
    subject_dict.extend(obj.data.get("subject_terms"))

    old_subjects_list = []
    for subj in subject_dict:
        old_subjects_list.append(subj["term"])

    obj.data["subject_terms"] = revised_subjects_list(old_subjects_list,
                                                      new_subjects_list,
                                                      subject_dict)
    obj.save()
    db.session.commit()
    return json_success_message('subjects')


def revised_subjects_list(old, new, subject_dict):
    """Using sets, it determines which elements to remove
    and which to add when editing the subjects.
    """
    to_remove = [str(x) for x in list(set(old) - set(new))]
    to_add = [str(x) for x in list(set(new) - set(old))]

    # Remove subjects
    subject_objects = [subj for subj in subject_dict
                       if subj["term"] not in to_remove]

    # Add the new subjects
    for subj in to_add:
        subject_objects.append({
            "term": subj,
            "scheme": "INSPIRE"
        })

    return subject_objects
