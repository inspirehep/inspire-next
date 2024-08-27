# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
from __future__ import absolute_import, division, print_function

from workflow.patterns.controlflow import IF_ELSE

from inspirehep.modules.literaturesuggest.tasks import curation_ticket_context
from inspirehep.modules.workflows.tasks.actions import (
    add_core, halt_record, is_core, link_institutions_with_affiliations,
    load_record_from_hep, normalize_author_affiliations,
    remove_inspire_categories_derived_from_core_arxiv_categories)
from inspirehep.modules.workflows.tasks.submission import create_ticket
from inspirehep.modules.workflows.tasks.upload import store_record
from inspirehep.modules.workflows.utils import do_not_repeat


class CoreSelection(object):
    """Workflow for changing coreness of the paper"""

    name = "CORE_SELECTION"
    data_type = "hep"

    workflow = (
        halt_record(
            action="core_selection_approval",
            message="Submission halted Waiting for curator to decide if record is CORE.",
        ),
        load_record_from_hep,
        add_core,
        IF_ELSE(
            is_core,
            [
                normalize_author_affiliations,
                link_institutions_with_affiliations,
                do_not_repeat("create_ticket_curator_core_publisher")(
                    create_ticket(
                        template="literaturesuggest/tickets/curation_core.html",
                        queue="HEP_curation",
                        context_factory=curation_ticket_context,
                        ticket_id_key="curation_ticket_id",
                    ),
                ),
                store_record,
            ],
            remove_inspire_categories_derived_from_core_arxiv_categories,
        ),
    )
