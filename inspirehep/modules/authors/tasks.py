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

from __future__ import absolute_import, division, print_function

import copy
import os

from datetime import date

from flask import current_app, url_for

from sqlalchemy.orm.exc import NoResultFound

from inspirehep.modules.forms.utils import filter_empty_elements

from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity

from .dojson.model import updateform


def formdata_to_model(obj, formdata):
    """Manipulate form data to match authors data model."""
    form_fields = copy.deepcopy(formdata)

    filter_empty_elements(
        form_fields,
        ['institution_history', 'advisors',
         'websites', 'experiments']
    )
    data = updateform.do(form_fields)

    # ======
    # Schema
    # ======
    if '$schema' not in data and '$schema' in obj.data:
        data['$schema'] = obj.data.get('$schema')

    if '$schema' in data and not data['$schema'].startswith('http'):
        data['$schema'] = url_for(
            'invenio_jsonschemas.get_schema',
            schema_path="records/{0}".format(data['$schema'])
        )

    author_name = ''

    if 'family_name' in form_fields and form_fields['family_name']:
        author_name = form_fields['family_name'].strip() + ', '
    if 'given_names' in form_fields and form_fields['given_names']:
        author_name += form_fields['given_names']

    if author_name:
        data.get('name', {})['value'] = author_name

    # Add comments to extra data
    if 'extra_comments' in form_fields and form_fields['extra_comments']:
        data.setdefault('_private_notes', []).append({
            'source': 'submitter',
            'value': form_fields['extra_comments']
        })

    data['stub'] = False

    # ==========
    # Submitter Info
    # ==========
    try:
        user_email = User.query.get(obj.id_user).email
    except AttributeError:
        user_email = ''
    try:
        orcid = UserIdentity.query.filter_by(
            id_user=obj.id_user,
            method='orcid'
        ).one()
    except NoResultFound:
        orcid = ''
    data['acquisition_source'] = dict(
        email=user_email,
        date=date.today().isoformat(),
        method="submitter",
        orcid=orcid,
        submission_number=str(obj.id),
        internal_uid=obj.id_user,
    )

    return data


def update_data_from_form(obj, eng):
    """Task to update data from formdata."""
    obj.data = formdata_to_model(obj, obj.extra_data['formdata'])


def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    return obj.extra_data.get("ticket", False)


def recreate_data(obj, eng):
    """Check if data needs to be recreated."""
    return obj.extra_data.get("recreate_data", False)


def new_ticket_context(user, obj):
    """Context for authornew new tickets."""
    subject = "Your suggestion to INSPIRE: author {0}".format(
        obj.data.get("name").get("preferred_name")
    )
    return dict(
        email=user.email,
        object=obj,
        subject=subject,
        user_comment=obj.extra_data.get('formdata', {}).get('extra_comments', ''),
    )


def update_ticket_context(user, obj):
    """Context for authornew new tickets."""
    subject = "Your update to author {0} on INSPIRE".format(
        obj.data.get("name").get("preferred_name")
    )
    record_url = os.path.join(current_app.config["AUTHORS_UPDATE_BASE_URL"], "record",
                              str(obj.data.get("control_number", "")))
    return dict(
        email=user.email,
        url=record_url,
        bibedit_url=record_url + "/edit",
        user_comment=obj.extra_data.get('formdata', {}).get('extra_comments', ''),
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
        user_comment=obj.extra_data.get('formdata', {}).get('extra_comments', ''),
    )
