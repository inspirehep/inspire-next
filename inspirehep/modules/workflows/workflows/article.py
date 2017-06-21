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

"""Workflow for processing single arXiv records harvested."""

from __future__ import absolute_import, division, print_function

from workflow.patterns.controlflow import (
    IF,
    IF_ELSE,
    IF_NOT,
)

from inspire_dojson.hep import hep2marc
from inspirehep.modules.workflows.tasks.refextract import extract_journal_info
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_fulltext_download,
    arxiv_package_download,
    arxiv_plot_extract,
    arxiv_derive_inspire_categories,
)
from inspirehep.modules.workflows.tasks.actions import (
    add_core,
    halt_record,
    is_record_relevant,
    in_production_mode,
    is_record_accepted,
    reject_record,
    is_experimental_paper,
    is_marked,
    is_submission,
    is_arxiv_paper,
    mark,
    prepare_update_payload,
    refextract,
    submission_fulltext_download,
)

from inspirehep.modules.workflows.tasks.classifier import (
    classify_paper,
    filter_core_keywords,
)
from inspirehep.modules.workflows.tasks.beard import guess_coreness
from inspirehep.modules.workflows.tasks.magpie import (
    guess_keywords,
    guess_categories,
    guess_experiments,
)
from inspirehep.modules.workflows.tasks.merging import (
    merge_articles,
    store_temporary_root,
    store_root,
)
from inspirehep.modules.workflows.tasks.merging import (
    is_an_update,
    is_not_an_update,
    is_an_update_with_conflicts,
)
from inspirehep.modules.workflows.tasks.matching import (
    delete_self_and_stop_processing,
    stop_processing,
    pending_in_holding_pen,
    article_exists,
    already_harvested,
    update_existing_workflow_object,
)
from inspirehep.modules.workflows.tasks.upload import store_record, set_schema
from inspirehep.modules.workflows.tasks.submission import (
    add_note_entry,
    close_ticket,
    create_ticket,
    filter_keywords,
    prepare_files,
    prepare_keywords,
    remove_references,
    reply_ticket,
    send_robotupload,
    wait_webcoll,
)

from inspirehep.modules.literaturesuggest.tasks import (
    curation_ticket_needed,
    reply_ticket_context,
    new_ticket_context,
    curation_ticket_context,
)


NOTIFY_SUBMISSION = [
    # Special RT integration for submissions
    # ======================================
    create_ticket(
        template="literaturesuggest/tickets/curator_submitted.html",
        queue="HEP_add_user",
        context_factory=new_ticket_context,
        ticket_id_key="ticket_id"
    ),
    reply_ticket(
        template="literaturesuggest/tickets/user_submitted.html",
        context_factory=reply_ticket_context,
        keep_new=True
    ),
]


ADD_INGESTION_MARKS = [
    # Article matching for non-submissions
    # ====================================
    # Query holding pen to see if we already have this article ingested
    #
    # NOTE on updates:
    #     If the same article has been harvested before and the
    #     ingestion has been completed, process is continued
    #     to allow for updates.
    IF(
        pending_in_holding_pen,
        [mark('delete', True)]
    ),
    IF(
        is_arxiv_paper,
        [
            # FIXME: This filtering step should be removed when this
            #        workflow includes arXiv CORE harvesting
            IF(
                already_harvested,
                [
                    mark('already-ingested', True),
                    mark('stop', True),
                ]
            ),
        ]
    ),
]


DELETE_AND_STOP_IF_NEEDED = [
    IF(
        is_marked('delete'),
        [
            update_existing_workflow_object,
            # TODO: Wen we get to fix refextract, we can remove the
            # following step as the references will be good enough to
            # trust
            delete_self_and_stop_processing
        ]
    ),
    IF(
        is_marked('stop'),
        [stop_processing]
    ),
]


ENHANCE_RECORD = [
    # Article Processing
    # ==================
    IF(
        is_arxiv_paper,
        [
            arxiv_fulltext_download,
            arxiv_package_download,
            arxiv_plot_extract,
            refextract,
            arxiv_derive_inspire_categories,
            arxiv_author_list("authorlist2marcxml.xsl"),
        ]
    ),
    IF(
        is_submission,
        [
            submission_fulltext_download,
            refextract,
        ]
    ),
    extract_journal_info,
    classify_paper(
        taxonomy="HEPont.rdf",
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
    ),
    filter_core_keywords,
    guess_categories,
    IF(
        is_experimental_paper,
        [guess_experiments]
    ),
    guess_keywords,
    # Predict action for a generic HEP paper based only on title
    # and abstract.
    guess_coreness,  # ("arxiv_skip_astro_title_abstract.pickle)
    # Check if we shall halt or auto-reject
    # =====================================
]


STOP_FOR_APPROVAL_OR_SOLVING_CONFLICTS = [
    IF_ELSE(
        is_record_relevant,
        [
            IF(
                # new records will be halted to be approved on coreness
                is_not_an_update,
                halt_record(
                    action="hep_approval",
                    message="Submission halted for curator approval.",
                )
            ),
            IF(
                # updates with conflicts will halt for solve conflicts
                is_an_update_with_conflicts,
                halt_record(
                    action="hep_approval",
                    message="Submission halted for resolving conflicts.",
                )
            ),
            # if it's an update without conflicts the workflow shouldn't stop
            mark('no-need-approval', True)
        ],
        [
            reject_record("Article automatically rejected"),
            stop_processing
        ]
    ),
]


NOTIFY_NOT_ACCEPTED = [
    IF(
        is_submission,
        [reply_ticket(context_factory=reply_ticket_context)]
    )
]


NOTIFY_ALREADY_EXISTING = [
    reject_record('Article was already found on INSPIRE'),
    stop_processing,
    reply_ticket(
        template=(
            "literaturesuggest/tickets/"
            "user_rejected_exists.html"
        ),
        context_factory=reply_ticket_context
    ),
    close_ticket(ticket_id_key="ticket_id"),
]


NOTIFY_USER_OR_CURATOR = [
    IF(
        is_submission,
        [
            reply_ticket(
                template='literaturesuggest/tickets/user_accepted.html',
                context_factory=reply_ticket_context,
            ),
        ],
    ),
    IF(
        curation_ticket_needed,
        [
            create_ticket(
                template='literaturesuggest/tickets/curation_core.html',
                queue='HEP_curation',
                context_factory=curation_ticket_context,
                ticket_id_key='curation_ticket_id',
            ),
        ],
    ),
]


POSTENHANCE_RECORD = [
    add_core,
    add_note_entry,
    filter_keywords,
    prepare_keywords,
    remove_references,
    prepare_files,
]


SEND_TO_LEGACY_AND_WAIT = [
    IF_ELSE(
        is_an_update,
        [
            prepare_update_payload(extra_data_key="update_payload"),
            send_robotupload(
                marcxml_processor=hep2marc,
                mode="correct",
                extra_data_key="update_payload"
            ),
        ], [
            send_robotupload(
                marcxml_processor=hep2marc,
                mode="insert"
            ),
            wait_webcoll,
        ]
    ),
]

CHECK_IF_MERGE = [
    store_temporary_root,
    IF(
        is_an_update,
        [
            IF_ELSE(
                is_submission,
                NOTIFY_ALREADY_EXISTING,
                [
                    merge_articles,
                    mark('merged', True)
                    # TODO: save record with new non-conflicting merged fields
                ]
            ),
        ],
    ),
]


ADD_MARKS = [
    # Query locally or via legacy search API to see if article
    # is already ingested and this is an update
    IF(
        article_exists,
        [
            mark('match-found', True),
            mark('is-update', True)
        ]
    ),
    IF(
        pending_in_holding_pen,
        [mark('already-in-holding-pen', True)],
    ),
    IF_ELSE(
        is_submission,
        NOTIFY_SUBMISSION,
        (
            ADD_INGESTION_MARKS
        )
    ),
]


class Article(object):
    """Article ingestion workflow for Literature collection."""
    name = "HEP"
    data_type = "hep"

    workflow = (
        [
            # Make sure schema is set for proper indexing in Holding Pen
            set_schema,
        ] +
        ADD_MARKS +
        DELETE_AND_STOP_IF_NEEDED +
        ENHANCE_RECORD +
        CHECK_IF_MERGE +
        STOP_FOR_APPROVAL_OR_SOLVING_CONFLICTS +
        [
            IF_ELSE(
                is_record_accepted,
                (
                    POSTENHANCE_RECORD +
                    SEND_TO_LEGACY_AND_WAIT +
                    NOTIFY_USER_OR_CURATOR +
                    [
                        # TODO: once legacy is out, this should become
                        # unconditional, and remove the SEND_TO_LEGACY_AND_WAIT
                        # steps
                        store_record,
                        store_root,
                    ]
                ),
                NOTIFY_NOT_ACCEPTED,
            ),
            IF(
                is_submission,
                [close_ticket(ticket_id_key="ticket_id")],
            )
        ]
    )
