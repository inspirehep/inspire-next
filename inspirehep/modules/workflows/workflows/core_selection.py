# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
from __future__ import absolute_import, division, print_function

from inspirehep.modules.literaturesuggest.tasks import curation_ticket_context
from inspirehep.modules.workflows.tasks.actions import halt_record, normalize_affiliations, \
    link_institutions_with_affiliations, load_record_from_hep
from inspirehep.modules.workflows.tasks.submission import prepare_keywords, create_ticket
from inspirehep.modules.workflows.tasks.upload import store_record
from inspirehep.modules.workflows.utils import do_not_repeat
from inspirehep.modules.workflows.workflows.article import SEND_TO_LEGACY


def set_core(obj, eng):
    obj.data['core'] = True
    return obj


class CoreSelection(object):
    """Workflow for changing coreness of the paper"""
    name = "CORE_SELECTION"
    data_type = "hep"

    workflow = (
        halt_record(
            action='hep_approval',
            message='Submission halted Waiting for curator to decide if record is CORE.'
        ),
        load_record_from_hep,
        set_core,
        prepare_keywords,
        normalize_affiliations,
        link_institutions_with_affiliations,
        do_not_repeat('create_ticket_curator_core_publisher')(
            create_ticket(
                template='literaturesuggest/tickets/curation_core.html',
                queue='HEP_publishing',
                context_factory=curation_ticket_context,
                ticket_id_key='curation_ticket_id',
            ),
        ),
        store_record,
        SEND_TO_LEGACY
    )
