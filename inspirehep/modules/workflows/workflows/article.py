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
    IF_NOT,
    IF_ELSE,
)

from inspirehep.modules.workflows.tasks.refextract import extract_journal_info
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_package_download,
    arxiv_plot_extract,
    arxiv_derive_inspire_categories,
    populate_arxiv_document,
)
from inspirehep.modules.workflows.tasks.actions import (
    add_core,
    count_reference_coreness,
    download_documents,
    error_workflow,
    fix_submission_number,
    halt_record,
    is_arxiv_paper,
    is_experimental_paper,
    is_marked,
    is_record_accepted,
    is_record_relevant,
    is_submission,
    mark,
    normalize_journal_titles,
    populate_journal_coverage,
    populate_submission_document,
    preserve_root,
    refextract,
    reject_record,
    save_workflow,
    set_refereed_and_fix_document_type,
    validate_record,
    jlab_ticket_needed,
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
from inspirehep.modules.workflows.tasks.matching import (
    stop_processing,
    raise_if_match_wf_in_error_or_initial,
    match_non_completed_wf_in_holdingpen,
    match_previously_rejected_wf_in_holdingpen,
    exact_match,
    fuzzy_match,
    is_fuzzy_match_approved,
    set_exact_match_as_approved_in_extradata,
    set_fuzzy_match_approved_in_extradata,
    has_same_source,
    stop_matched_holdingpen_wfs,
    auto_approve,
    set_core_in_extra_data,
)
from inspirehep.modules.workflows.tasks.merging import (
    has_conflicts,
    merge_articles,
)
from inspirehep.modules.workflows.tasks.upload import (
    set_schema,
    store_record,
    store_root,
)
from inspirehep.modules.workflows.tasks.submission import (
    close_ticket,
    create_ticket,
    filter_keywords,
    prepare_keywords,
    reply_ticket,
    send_to_legacy,
    wait_webcoll,
)

from inspirehep.modules.literaturesuggest.tasks import (
    curation_ticket_needed,
    reply_ticket_context,
    new_ticket_context,
    curation_ticket_context,
)


NOTIFY_SUBMISSION = [
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

CHECK_AUTO_APPROVE = [
    IF_ELSE(
        is_submission,
        mark('auto-approved', False),
        IF_ELSE(
            auto_approve,
            [
                mark('auto-approved', True),
                set_core_in_extra_data,
            ],
            mark('auto-approved', False),
        ),
    ),
]

ENHANCE_RECORD = [
    IF(
        is_arxiv_paper,
        [
            populate_arxiv_document,
            arxiv_package_download,
            arxiv_plot_extract,
            arxiv_derive_inspire_categories,
            arxiv_author_list("authorlist2marcxml.xsl"),
        ]
    ),
    IF(
        is_submission,
        populate_submission_document,
    ),
    download_documents,
    normalize_journal_titles,
    refextract,
    count_reference_coreness,
    extract_journal_info,
    populate_journal_coverage,
    classify_paper(
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
    ),
    filter_core_keywords,
    guess_categories,
    IF(
        is_experimental_paper,
        guess_experiments,
    ),
    guess_keywords,
    guess_coreness,
]


NOTIFY_NOT_ACCEPTED = [
    IF(
        is_submission,
        reply_ticket(context_factory=reply_ticket_context),
    )
]


NOTIFY_ALREADY_EXISTING = [
    reject_record('Article was already found on INSPIRE'),
    mark('approved', False),
    reply_ticket(
        template=(
            "literaturesuggest/tickets/"
            "user_rejected_exists.html"
        ),
        context_factory=reply_ticket_context
    ),
    close_ticket(ticket_id_key="ticket_id"),
    save_workflow,
    stop_processing,
]


NOTIFY_ACCEPTED = [
    IF(
        is_submission,
        reply_ticket(
            template='literaturesuggest/tickets/user_accepted.html',
            context_factory=reply_ticket_context,
        ),
    ),
]


NOTIFY_CURATOR_IF_NEEDED = [
    IF_NOT(
        is_marked('is-update'),
        [
            IF_ELSE(
                jlab_ticket_needed,
                create_ticket(
                    template='literaturesuggest/tickets/curation_jlab.html',
                    queue='HEP_curation_jlab',
                    context_factory=curation_ticket_context,
                    ticket_id_key='curation_ticket_id',
                ),
                IF(
                    curation_ticket_needed,
                    create_ticket(
                        template='literaturesuggest/tickets/curation_core.html',
                        queue='HEP_curation',
                        context_factory=curation_ticket_context,
                        ticket_id_key='curation_ticket_id',
                    ),
                ),
            )
        ]
    ),
]


POSTENHANCE_RECORD = [
    add_core,
    filter_keywords,
    prepare_keywords,
    set_refereed_and_fix_document_type,
    fix_submission_number,
]


SEND_TO_LEGACY = [
    send_to_legacy,
]


WAIT_FOR_LEGACY_WEBCOLL = [
    IF_NOT(
        is_marked('is-update'),
        wait_webcoll,
    ),
]


STOP_IF_EXISTING_SUBMISSION = [
    IF(
        is_submission,
        IF(
            is_marked('is-update'),
            NOTIFY_ALREADY_EXISTING
        )
    )
]


HALT_FOR_APPROVAL_IF_NEW_OR_STOP_IF_NOT_RELEVANT = [
    IF_NOT(
        is_record_relevant,
        [
            reject_record('Article automatically rejected'),
            mark('approved', False),
            save_workflow,
            stop_processing,
        ],
    ),
    preserve_root,
    IF_ELSE(
        is_marked('is-update'),
        [
            merge_articles,
            IF(
                has_conflicts,
                halt_record(
                    action='merge_approval',
                    message='Submission halted for merging conflicts.'
                ),
            ),
            mark('approved', True),
            mark('merged', True),
        ],
        IF_ELSE(
            is_marked('auto-approved'),
            mark('approved', True),
            halt_record(
                action="hep_approval",
                message="Submission halted for curator approval.",
            )
        ),
    ),
]


STORE_RECORD = [
    store_record,
    store_root,
]


MARK_IF_MATCH_IN_HOLDINGPEN = [
    raise_if_match_wf_in_error_or_initial,
    IF_ELSE(
        match_non_completed_wf_in_holdingpen,
        [
            mark('already-in-holding-pen', True),
            save_workflow,
        ],
        mark('already-in-holding-pen', False),
    ),

    IF_ELSE(
        match_previously_rejected_wf_in_holdingpen,
        [
            mark('previously_rejected', True),
            save_workflow,
        ],
        mark('previously_rejected', False),
    )
]


ERROR_WITH_UNEXPECTED_WORKFLOW_PATH = [
    mark('unexpected-workflow-path', True),
    error_workflow('Unexpected workflow path.'),
    save_workflow,
]


# Currently we handle harvests as if all were arxiv, that will have to change.
PROCESS_HOLDINGPEN_MATCH_HARVEST = [
    IF_NOT(
        is_marked('is-update'),
        IF(
            is_marked('previously_rejected'),
            IF_NOT(
                is_marked('auto-approved'),
                IF(
                    has_same_source('previously_rejected_matches'),
                    [
                        mark('approved', False),  # auto-reject
                        save_workflow,
                        stop_processing,
                    ],
                )
            ),
        ),
    ),

    IF_ELSE(
        is_marked('already-in-holding-pen'),
        IF_ELSE(
            has_same_source('holdingpen_matches'),
            # stop the matched wf and continue this one
            [
                stop_matched_holdingpen_wfs,
                mark('stopped-matched-holdingpen-wf', True),
            ],
            [
                # else, it's an update from another source
                # keep the old one
                mark('stopped-matched-holdingpen-wf', False),
                save_workflow,
                stop_processing
            ],
        ),
        mark('stopped-matched-holdingpen-wf', False),
    ),
    save_workflow,
]


PROCESS_HOLDINGPEN_MATCH_SUBMISSION = [
    IF(
        is_marked('already-in-holding-pen'),
        IF_ELSE(
            has_same_source('holdingpen_matches'),
            # form should detect this double submission
            ERROR_WITH_UNEXPECTED_WORKFLOW_PATH,

            # stop the matched wf and continue this one
            [
                stop_matched_holdingpen_wfs,
                mark('stopped-matched-holdingpen-wf', True),
                save_workflow
            ],

        )
    )
]


PROCESS_HOLDINGPEN_MATCHES = [
    IF_ELSE(
        is_submission,
        PROCESS_HOLDINGPEN_MATCH_SUBMISSION,
        PROCESS_HOLDINGPEN_MATCH_HARVEST,
    )
]


CHECK_IS_UPDATE = [
    IF_ELSE(
        exact_match,
        [
            set_exact_match_as_approved_in_extradata,
            mark('is-update', True),
            mark('exact-matched', True),
        ],
        IF_ELSE(
            fuzzy_match,
            [
                halt_record(
                    action="match_approval",
                    message="Halted for matching approval.",
                ),
                IF_ELSE(
                    is_fuzzy_match_approved,
                    [
                        set_fuzzy_match_approved_in_extradata,
                        mark('fuzzy-matched', True),
                        mark('is-update', True),
                    ],
                    mark('is-update', False),
                )
            ],
            mark('is-update', False),
        )
    ),
    save_workflow,
]


NOTIFY_IF_SUBMISSION = [
    IF(
        is_submission,
        NOTIFY_SUBMISSION,
    )
]


INIT_MARKS = [
    mark('auto-approved', None),
    mark('already-in-holding-pen', None),
    mark('previously_rejected', None),
    mark('is-update', None),
    mark('stopped-matched-holdingpen-wf', None),
    mark('approved', None),
    mark('unexpected-workflow-path', None),
    save_workflow
]


PRE_PROCESSING = [
    # Make sure schema is set for proper indexing in Holding Pen
    set_schema,
    INIT_MARKS,
    validate_record('hep')
]


class Article(object):
    """Article ingestion workflow for Literature collection."""
    name = "HEP"
    data_type = "hep"

    workflow = (
        PRE_PROCESSING +
        NOTIFY_IF_SUBMISSION +
        MARK_IF_MATCH_IN_HOLDINGPEN +
        CHECK_IS_UPDATE +
        STOP_IF_EXISTING_SUBMISSION +
        CHECK_AUTO_APPROVE +
        PROCESS_HOLDINGPEN_MATCHES +
        ENHANCE_RECORD +
        HALT_FOR_APPROVAL_IF_NEW_OR_STOP_IF_NOT_RELEVANT +
        [
            IF_ELSE(
                is_record_accepted,
                (
                    POSTENHANCE_RECORD +
                    STORE_RECORD +
                    SEND_TO_LEGACY +
                    WAIT_FOR_LEGACY_WEBCOLL +
                    NOTIFY_ACCEPTED +
                    NOTIFY_CURATOR_IF_NEEDED
                ),
                NOTIFY_NOT_ACCEPTED,
            ),
            IF(
                is_submission,
                close_ticket(ticket_id_key="ticket_id"),
            )
        ]
    )
