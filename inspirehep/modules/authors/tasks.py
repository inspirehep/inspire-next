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

from __future__ import absolute_import, division, print_function

import os

from flask import current_app

from inspirehep.modules.forms.utils import get_user_comments
from inspirehep.modules.workflows.utils import with_debug_logging


@with_debug_logging
def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    return obj.extra_data.get("ticket", False)


def new_ticket_context(user, obj):
    """Context for authornew new tickets."""
    subject = u"Your suggestion to INSPIRE: author {0}".format(
        obj.data.get("name").get("preferred_name")
    )
    return dict(
        email=user.email,
        object=obj,
        subject=subject,
        user_comment='\n'.join(
            get_user_comments(private_notes=obj.data.get('_private_notes', []))
        ),
    )


def update_ticket_context(user, obj):
    """Context for authornew new tickets."""
    subject = u"Your update to author {0} on INSPIRE".format(
        obj.data.get("name").get("preferred_name")
    )
    record_url = os.path.join(
        current_app.config["AUTHORS_UPDATE_BASE_URL"],
        "record",
        str(obj.data.get("control_number", "")),
    )
    return dict(
        email=user.email,
        url=record_url,
        bibedit_url=record_url + "/edit",
        subject=subject,
        user_comment='\n'.join(
            get_user_comments(private_notes=obj.data.get('_private_notes', []))
        ),
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
    subject = u"Curation needed for author {0} {1}".format(
        obj.data.get("name").get("preferred_name"),
        bai
    )
    return dict(
        email=user.email,
        object=obj,
        recid=recid,
        subject=subject,
        record_url=record_url,
        user_comment='\n'.join(
            get_user_comments(private_notes=obj.data.get('_private_notes', []))
        ),
    )
