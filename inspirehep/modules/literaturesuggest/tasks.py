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

from idutils import is_arxiv_post_2007

from inspire_utils.record import get_value
from inspirehep.modules.workflows.utils import with_debug_logging
from inspirehep.utils.record import get_title


def _get_user_comment(workflow_object):
    user_comment = next(
        (
            note.get('value')
            for note in workflow_object.data.get('_private_notes', [])
            if note.get('source') == 'submitter'
        ),
        '',
    )

    return user_comment


def new_ticket_context(user, obj):
    """Context for literature new tickets."""
    title = get_title(obj.data)
    subject = u"Your suggestion to INSPIRE: {0}".format(title)
    user_comment = _get_user_comment(obj)
    identifiers = get_value(obj.data, "external_system_numbers.value") or []
    return dict(
        email=user.email,
        title=title,
        identifier=identifiers or "",
        user_comment=user_comment,
        object=obj,
        subject=subject
    )


def reply_ticket_context(user, obj):
    """Context for literature replies."""
    return dict(
        object=obj,
        user=user,
        title=get_title(obj.data),
        reason=obj.extra_data.get("reason", ""),
        record_url=obj.extra_data.get("url", ""),
    )


def curation_ticket_context(user, obj):
    recid = obj.extra_data.get('recid')
    record_url = obj.extra_data.get('url')

    arxiv_ids = get_value(obj.data, 'arxiv_eprints.value') or []
    for index, arxiv_id in enumerate(arxiv_ids):
        if arxiv_id and is_arxiv_post_2007(arxiv_id):
            arxiv_ids[index] = 'arXiv:{0}'.format(arxiv_id)

    report_numbers = get_value(obj.data, 'report_numbers.value') or []
    dois = [
        "doi:{0}".format(doi)
        for doi in get_value(obj.data, 'dois.value') or []
    ]
    link_to_pdf = obj.extra_data.get('submission_pdf')

    subject = ' '.join(filter(
        lambda x: x is not None,
        arxiv_ids + dois + report_numbers + ['(#{0})'.format(recid)]
    ))

    user_comment = _get_user_comment(obj)

    return dict(
        recid=recid,
        record_url=record_url,
        link_to_pdf=link_to_pdf,
        email=user.email,
        user_comment=user_comment,
        subject=subject
    )


@with_debug_logging
def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    return obj.extra_data.get("core", False)
