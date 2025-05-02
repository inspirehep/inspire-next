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
    populate_arxiv_document,
)
from inspirehep.modules.workflows.tasks.actions import (
    add_core,
    count_reference_coreness,
    download_documents,
    error_workflow,
    fix_submission_number,
    go_to_first_step,
    halt_record,
    increase_restart_count_or_error,
    is_arxiv_paper,
    is_experimental_paper,
    is_marked,
    is_record_accepted,
    is_record_relevant,
    is_submission,
    load_from_source_data,
    mark,
    normalize_journal_titles,
    populate_journal_coverage,
    populate_submission_document,
    preserve_root,
    refextract,
    reject_record,
    save_workflow,
    set_refereed_and_fix_document_type,
    update_inspire_categories,
    validate_record,
    jlab_ticket_needed,
    delay_if_necessary,
    should_be_hidden,
    replace_collection_to_hidden,
    is_suitable_for_pdf_authors_extraction,
    extract_authors_from_pdf,
    is_fermilab_report,
    add_collection,
    normalize_collaborations,
    normalize_author_affiliations,
    is_core,
    create_core_selection_wf,
    check_if_france_in_fulltext,
    check_if_france_in_raw_affiliations,
    check_if_germany_in_fulltext,
    check_if_germany_in_raw_affiliations,
    link_institutions_with_affiliations,
    check_if_uk_in_fulltext,
    check_if_uk_in_raw_affiliations,
    check_if_cern_candidate,
)

from inspirehep.modules.workflows.tasks.classifier import (
    classify_paper,
    filter_core_keywords,
    guess_coreness,
)
from inspirehep.modules.workflows.tasks.magpie import (
    guess_keywords,
    guess_categories,
    guess_experiments,
)
from inspirehep.modules.workflows.tasks.matching import (
    handle_matched_holdingpen_wfs,
    stop_processing,
    exact_match,
    fuzzy_match,
    is_fuzzy_match_approved,
    set_exact_match_as_approved_in_extradata,
    set_fuzzy_match_approved_in_extradata,
    has_same_source,
    auto_approve,
    run_next_if_necessary,
    set_core_in_extra_data,
    has_more_than_one_exact_match,
    raise_if_match_workflow,
    match_previously_rejected_wf_in_holdingpen,
    match_non_completed_wf_in_holdingpen,
)
from inspirehep.modules.workflows.tasks.merging import (
    has_conflicts,
    merge_articles,
    conflicts_ticket_context,
)
from inspirehep.modules.workflows.tasks.upload import (
    is_stale_data,
    set_schema,
    store_record,
    store_root,
)
from inspirehep.modules.workflows.tasks.submission import (
    close_ticket,
    create_ticket,
    filter_keywords,
    reply_ticket,
    send_to_legacy,
)
from inspirehep.modules.workflows.utils import do_not_repeat
from inspirehep.modules.literaturesuggest.tasks import (
    curation_ticket_needed,
    check_source_publishing,
    reply_ticket_context,
    new_ticket_context,
    curation_ticket_context,
)


NOTIFY_SUBMISSION = [
    do_not_repeat("create_ticket_curator_new_submission")(
        create_ticket(
            template="literaturesuggest/tickets/curator_submitted.html",
            queue="HEP_add_user",
            context_factory=new_ticket_context,
            ticket_id_key="ticket_id",
        ),
    ),
    do_not_repeat("reply_ticket_user_new_submission")(
        reply_ticket(
            template="literaturesuggest/tickets/user_submitted.html",
            context_factory=reply_ticket_context,
            keep_new=True,
        ),
    ),
]

CHECK_AUTO_APPROVE = [
    IF_ELSE(
        is_submission,
        mark("auto-approved", False),
        IF_ELSE(
            auto_approve,
            [
                mark("auto-approved", True),
                IF_NOT(
                    is_marked("is-update"),
                    set_core_in_extra_data,
                ),
            ],
            mark("auto-approved", False),
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
            arxiv_author_list,
        ],
    ),
    IF(
        is_submission,
        populate_submission_document,
    ),
    download_documents,
    IF(
        is_suitable_for_pdf_authors_extraction,
        extract_authors_from_pdf,
    ),
    normalize_journal_titles,
    save_workflow,
    refextract,
    save_workflow,
    count_reference_coreness,
    extract_journal_info,
    save_workflow,
    populate_journal_coverage,
    save_workflow,
    classify_paper(
        only_core_tags=False,
        spires=True,
        with_author_keywords=True,
    ),
    save_workflow,
    filter_core_keywords,
    guess_categories,
    save_workflow,
    IF(
        is_experimental_paper,
        guess_experiments,
    ),
    guess_keywords,
    guess_coreness,
    normalize_collaborations,
    save_workflow,
]


NOTIFY_AND_CLOSE_NOT_ACCEPTED = [
    IF(
        is_submission,
        do_not_repeat("close_ticket_submission_not_accepted")(
            close_ticket(
                ticket_id_key="ticket_id", context_factory=reply_ticket_context
            ),
        ),
    )
]


NOTIFY_AND_CLOSE_ALREADY_EXISTING = [
    reject_record("Article was already found on INSPIRE"),
    mark("approved", False),
    do_not_repeat("close_ticket_user_submission_already_in_inspire")(
        close_ticket(
            ticket_id_key="ticket_id",
            template=("literaturesuggest/tickets/user_rejected_exists.html"),
            context_factory=reply_ticket_context,
        ),
    ),
    save_workflow,
    stop_processing,
]


NOTIFY_AND_CLOSE_ACCEPTED = [
    IF(
        is_submission,
        do_not_repeat("close_ticket_user_submission_accepted")(
            close_ticket(
                ticket_id_key="ticket_id",
                template="literaturesuggest/tickets/user_accepted.html",
                context_factory=reply_ticket_context,
            ),
        ),
    ),
]


NOTIFY_CURATOR_IF_NEEDED = [
    IF_NOT(
        is_marked("is-update"),
        IF_ELSE(
            is_arxiv_paper,
            [
                IF(
                    check_if_france_in_fulltext,
                    create_ticket(
                        template="literaturesuggest/tickets/curation_core.html",
                        queue="HAL_curation",
                        context_factory=curation_ticket_context,
                        ticket_id_key="curation_ticket_id",
                    ),
                ),
                IF(
                    is_core,
                    [
                        IF(
                            check_if_germany_in_fulltext,
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="GER_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),
                        IF(
                            check_if_uk_in_fulltext,
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="UK_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),
                    ],
                ),
            ],
            [
                IF(
                    check_if_france_in_raw_affiliations,
                    create_ticket(
                        template="literaturesuggest/tickets/curation_core.html",
                        queue="HAL_curation",
                        context_factory=curation_ticket_context,
                        ticket_id_key="curation_ticket_id",
                    ),
                ),
                IF(
                    is_core,
                    [
                        IF(
                            check_if_germany_in_raw_affiliations,
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="GER_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),
                        IF(
                            check_if_uk_in_raw_affiliations,
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="UK_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),
                        IF(
                            check_if_cern_candidate,
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="CERN_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ),
    IF_NOT(
        is_marked("is-update"),
        [
            IF_ELSE(
                jlab_ticket_needed,
                do_not_repeat("create_ticket_jlab_curation")(
                    create_ticket(
                        template="literaturesuggest/tickets/curation_jlab.html",
                        queue="HEP_curation_jlab",
                        context_factory=curation_ticket_context,
                        ticket_id_key="curation_ticket_id",
                    ),
                ),
                IF(
                    curation_ticket_needed,  # if core
                    IF_ELSE(
                        # if it is coming from publisher, create ticket in hep_publisher queue
                        check_source_publishing,
                        do_not_repeat("create_ticket_curator_core_publisher")(
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="HEP_publishing",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),  # Otherwise create ticket in hep_curation queue
                        do_not_repeat("create_ticket_curator_core_curation")(
                            create_ticket(
                                template="literaturesuggest/tickets/curation_core.html",
                                queue="HEP_curation",
                                context_factory=curation_ticket_context,
                                ticket_id_key="curation_ticket_id",
                            ),
                        ),
                    ),
                ),
            )
        ],
    ),
]


POSTENHANCE_RECORD = [
    IF_NOT(
        is_marked("is-update"),
        add_core,
    ),
    filter_keywords,
    set_refereed_and_fix_document_type,
    fix_submission_number,
    IF(is_core, normalize_author_affiliations),
    link_institutions_with_affiliations,
    IF(
        is_fermilab_report,
        add_collection("Fermilab"),
    ),
    validate_record("hep"),
]


SEND_TO_LEGACY = [
    send_to_legacy(priority_config_key="LEGACY_ROBOTUPLOAD_PRIORITY_ARTICLE"),
]


STOP_IF_EXISTING_SUBMISSION = [
    IF(is_submission, IF(is_marked("is-update"), NOTIFY_AND_CLOSE_ALREADY_EXISTING))
]


HALT_FOR_APPROVAL_IF_NEW_OR_REJECT_IF_NOT_RELEVANT = [
    preserve_root,
    IF_ELSE(
        is_marked("is-update"),
        [
            merge_articles,
            IF(
                has_conflicts,
                [
                    create_ticket(
                        template="workflows/tickets/conflicts-ticket-template.html",
                        queue="HEP_conflicts",
                        ticket_id_key="conflict-ticket-id",
                        context_factory=conflicts_ticket_context,
                    ),
                    halt_record(
                        action="merge_approval",
                        message="Submission halted for merging conflicts.",
                    ),
                    close_ticket(ticket_id_key="conflict-ticket-id"),
                ],
            ),
            mark("approved", True),
            mark("merged", True),
        ],
        [
            update_inspire_categories,
            IF_ELSE(
                is_marked("auto-approved"),
                mark("approved", True),
                [
                    IF(
                        is_record_relevant,
                        halt_record(
                            action="hep_approval",
                            message="Submission halted for curator approval.",
                        ),
                    ),
                    IF_NOT(
                        is_marked("approved"),
                        IF_ELSE(
                            should_be_hidden,
                            [
                                replace_collection_to_hidden,
                                mark("approved", True),
                            ],
                            [
                                mark("approved", False),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    ),
    save_workflow,
]


STORE_RECORD = [
    IF(is_stale_data, go_to_first_step),
    store_record,
]


STORE_ROOT = [
    store_root,
]


MARK_IF_MATCH_IN_HOLDINGPEN = [
    raise_if_match_workflow,
    IF_ELSE(
        match_non_completed_wf_in_holdingpen,
        [
            mark("already-in-holding-pen", True),
            save_workflow,
        ],
        mark("already-in-holding-pen", False),
    ),
    IF_ELSE(
        match_previously_rejected_wf_in_holdingpen,
        [
            mark("previously_rejected", True),
            save_workflow,
        ],
        mark("previously_rejected", False),
    ),
]


ERROR_WITH_UNEXPECTED_WORKFLOW_PATH = [
    mark("unexpected-workflow-path", True),
    error_workflow("Unexpected workflow path."),
    save_workflow,
]


# Currently we handle harvests as if all were arxiv, that will have to change.
PROCESS_HOLDINGPEN_MATCH_HARVEST = [
    IF_NOT(
        is_marked("is-update"),
        IF(
            is_marked("previously_rejected"),
            IF_NOT(
                is_marked("auto-approved"),
                IF(
                    has_same_source("previously_rejected_matches"),
                    [
                        mark("approved", False),  # auto-reject
                        save_workflow,
                        stop_processing,
                        run_next_if_necessary,
                    ],
                ),
            ),
        ),
    ),
    IF_ELSE(
        is_marked("already-in-holding-pen"),
        [
            handle_matched_holdingpen_wfs,
            IF_ELSE(
                has_same_source("holdingpen_matches"),
                mark("stopped-matched-holdingpen-wf", True),
                mark("stopped-matched-holdingpen-wf", False),
            ),
        ],
        mark("stopped-matched-holdingpen-wf", False),
    ),
    save_workflow,
]


PROCESS_HOLDINGPEN_MATCH_SUBMISSION = [
    IF_ELSE(
        has_same_source("holdingpen_matches"),
        # form should detect this double submission
        ERROR_WITH_UNEXPECTED_WORKFLOW_PATH,
        # stop the matched wf and continue this one
        [
            handle_matched_holdingpen_wfs,
            mark("stopped-matched-holdingpen-wf", False),
            save_workflow,
        ],
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
            mark("is-update", True),
            mark("exact-matched", True),
            IF(
                has_more_than_one_exact_match,
                halt_record(
                    action="resolve_multiple_exact_matches",
                    message="Workflow halted for resolving multiple exact matches.",
                ),
            ),
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
                        mark("fuzzy-matched", True),
                        mark("is-update", True),
                    ],
                    mark("is-update", False),
                ),
            ],
            mark("is-update", False),
        ),
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
    mark("auto-approved", None),
    mark("already-in-holding-pen", None),
    mark("previously_rejected", None),
    mark("is-update", None),
    mark("stopped-matched-holdingpen-wf", None),
    mark("approved", None),
    mark("unexpected-workflow-path", None),
    mark("halted-by-match-with-different-source", None),
    do_not_repeat("marks")(mark("restart-count", 0)),
    save_workflow,
]


PRE_PROCESSING = [
    delay_if_necessary,
    load_from_source_data,
    increase_restart_count_or_error,
    # Make sure schema is set for proper indexing in Holding Pen
    set_schema,
    INIT_MARKS,
    validate_record("hep"),
]

FIND_NEXT_AND_RUN_IF_NECESSARY = [run_next_if_necessary]


CREATE_CORE_SELECTION_WF = [
    create_core_selection_wf,
]


class Article(object):
    """Article ingestion workflow for Literature collection."""

    name = "HEP"
    data_type = "hep"

    workflow = (
        PRE_PROCESSING
        + NOTIFY_IF_SUBMISSION
        + MARK_IF_MATCH_IN_HOLDINGPEN
        + CHECK_IS_UPDATE
        + STOP_IF_EXISTING_SUBMISSION
        + CHECK_AUTO_APPROVE
        + PROCESS_HOLDINGPEN_MATCHES
        + ENHANCE_RECORD
        + HALT_FOR_APPROVAL_IF_NEW_OR_REJECT_IF_NOT_RELEVANT
        + [
            IF_ELSE(
                is_record_accepted,
                (
                    POSTENHANCE_RECORD
                    + STORE_RECORD
                    + SEND_TO_LEGACY
                    + STORE_ROOT
                    + NOTIFY_AND_CLOSE_ACCEPTED
                    + NOTIFY_CURATOR_IF_NEEDED
                    + CREATE_CORE_SELECTION_WF
                ),
                NOTIFY_AND_CLOSE_NOT_ACCEPTED,
            ),
        ]
        + FIND_NEXT_AND_RUN_IF_NECESSARY
    )
