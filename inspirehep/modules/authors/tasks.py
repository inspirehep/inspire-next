# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

import os
import copy

from datetime import date
from functools import wraps
from flask import current_app, render_template

from invenio_accounts.models import User
from workflow.errors import WorkflowError

from inspirehep.modules.forms.utils import filter_empty_elements
from inspirehep.modules.workflows.tasks.submission import submit_rt_ticket


from .dojson.model import updateform


def convert_data_to_model(obj, eng):
    """Manipulate form data to match author model keys."""
    # Save original form data for later access
    form_fields = copy.deepcopy(obj.data)
    obj.extra_data["formdata"] = copy.deepcopy(form_fields)

    filter_empty_elements(
        obj.data,
        ['institution_history', 'advisors',
         'websites', 'experiments']
    )
    converted = updateform.do(obj.data)
    obj.data.update(converted)

    author_name = ''

    if 'family_name' in form_fields and form_fields['family_name']:
        author_name = form_fields['family_name'].strip() + ', '
    if 'given_names' in form_fields and form_fields['given_names']:
        author_name += form_fields['given_names']

    if author_name:
        obj.data.get('name', {})['value'] = author_name

    # Add comments to extra data
    if "comments" in form_fields and form_fields["comments"]:
        obj.extra_data["comments"] = form_fields["comments"]
        obj.data["_private_note"] = form_fields["comments"]

    # Add HEPNAMES collection
    obj.data["collections"] = [{
        "primary": "HEPNAMES"
    }]

    # ==========
    # Owner Info
    # ==========
    try:
        user_email = User.query.get(obj.id_user).email
    except AttributeError:
        user_email = ''
    sources = ["{0}{1}".format('inspire:uid:', obj.id_user)]
    obj.data['acquisition_source'] = dict(
        source=sources,
        email=user_email,
        date=date.today().isoformat(),
        method="submission",
        submission_number=obj.id,
    )


def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    return obj.extra_data.get("ticket", False)


def recreate_data(obj, eng):
    """Check if data needs to be recreated."""
    extra_data = obj.get_extra_data()
    return extra_data.get("recreate_data", False)


def new_ticket_context(user, obj):
    """Context for authornew new tickets."""
    subject = "Your suggestion to INSPIRE: author {0}".format(
        obj.data.get("name").get("preferred_name")
    )
    return dict(
        email=user.email,
        object=obj,
        subject=subject,
        user_comment=obj.extra_data.get("comments", ""),
    )


def update_ticket_context(user, obj):
    """Context for authornew new tickets."""
    recid = obj.data.get("recid", "")

    subject = "Your update to author {0} on INSPIRE".format(
        obj.data.get("name").get("preferred_name")
    )
    record_url = os.path.join(current_app.config["AUTHORS_UPDATE_BASE_URL"], "record",
                              str(recid))
    return dict(
        email=user.email,
        url=record_url,
        bibedit_url=record_url + "/edit",
        user_comment=obj.extra_data.get("comments", ""),
    )


def reply_ticket_context(user, obj):
    """Context for authornew replies."""
    return dict(
        object=obj,
        user=user,
        author_name=obj.data.get("name").get("preferred_name"),
        reason=obj.extra_data.get("reason", ""),
        record_url=obj.extra_data.get("url", ""),
    )


def curation_ticket_context(user, obj):
    """Context for authornew replies."""
    recid = obj.extra_data.get('recid')
    record_url = obj.extra_data.get('url')
    bai = ""
    if obj.data.get("bai"):
        bai = "[{}]".format(obj.data.get("bai"))
    subject = "Curation needed for author {0} {1}".format(
        obj.data.get("name").get("preferred_name"),
        bai
    )
    return dict(
        email=user.email,
        object=obj,
        recid=recid,
        subject=subject,
        record_url=record_url,
        user_comment=obj.extra_data.get("comments", ""),
    )
