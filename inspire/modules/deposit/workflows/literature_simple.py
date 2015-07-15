# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

from invenio.modules.deposit.tasks import (
    render_form,
    prepare_sip,
    prefill_draft,
    process_sip_metadata,
    # upload_record_sip
)

from .literature import literature


class literature_simple(literature):

    """Literature deposit submission without approval."""

    workflow = [
        # Pre-fill draft with values passed in from request
        prefill_draft(draft_id='default'),
        # Render form and wait for user to submit
        render_form(draft_id='default'),
        # Create the submission information package by merging form data
        # from all drafts (in this case only one draft exists).
        prepare_sip(),
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        # Generate MARC based on metadata dictionary.
        # finalize_record_sip(is_dump=False),
        # Upload the marcxml locally (good for debugging)
        # upload_record_sip(),
    ]

    name = "Literature (No approval)"
    name_plural = "Literature (No approval) submissions"
