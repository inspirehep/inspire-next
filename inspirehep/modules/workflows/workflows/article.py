# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Workflow for processing single arXiv records harvested."""

from workflow.patterns.controlflow import IF, IF_ELSE

from inspirehep.dojson.hep import hep2marc

from inspirehep.modules.refextract.tasks import extract_journal_info
from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_fulltext_download,
    arxiv_plot_extract,
    arxiv_refextract,
)
from inspirehep.modules.workflows.tasks.actions import (
    add_core,
    halt_record,
    is_record_relevant,
    shall_push_remotely,
    is_record_accepted,
    reject_record,
    is_experimental_paper,
    is_marked,
    is_submission,
    is_arxiv_paper,
    mark,
    emit_record_signals,
    prepare_update_payload
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
from inspirehep.modules.workflows.tasks.matching import(
    delete_self_and_stop_processing,
    stop_processing,
    pending_in_holding_pen,
    article_exists,
    already_harvested,
    previously_rejected,
    update_old_object,
)
from inspirehep.modules.workflows.tasks.upload import store_record, set_schema
from inspirehep.modules.workflows.tasks.submission import (
    send_robotupload,
    create_ticket,
    reply_ticket,
    add_note_entry,
    user_pdf_get,
    close_ticket, filter_keywords)

from inspirehep.modules.literaturesuggest.tasks import (
    curation_ticket_needed,
    reply_ticket_context,
    new_ticket_context,
    curation_ticket_context,
)


class Article(object):
    """Article ingestion workflow for Literature collection."""
    name = "HEP"
    data_type = "hep"

    workflow = [
        # Make sure schema is set for proper indexing in Holding Pen
        set_schema,
        # Emit record signals to receive metadata enrichment
        emit_record_signals,
        # Query locally or via legacy search API to see if article
        # is already ingested and this is an update
        IF(article_exists, [
            mark('match-found', True),
        ]),
        IF_ELSE(is_submission, [
            # Article matching for submissions
            # ================================
            IF(pending_in_holding_pen, [
                mark('already-in-holding-pen', True),
            ]),
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
        ], [
            # Article matching for non-submissions
            # ====================================
            # Query holding pen to see if we already have this article ingested
            #
            # NOTE on updates:
            #     If the same article has been harvested before and the
            #     ingestion has been completed, process is continued
            #     to allow for updates.
            IF(pending_in_holding_pen, [
                mark('already-in-holding-pen', True),
                mark('delete', True),
            ]),
            IF(is_arxiv_paper, [
                # FIXME: This filtering step should be removed when this
                #        workflow includes arXiv CORE harvesting
                IF(already_harvested, [
                    mark('already-ingested', True),
                    mark('stop', True),
                ]),
                # FIXME: This filtering step should be removed when:
                #        old previously rejected records are treated
                #        differently e.g. good auto-reject heuristics or better
                #        time based filtering (5 days is quite random now).
                IF(previously_rejected(), [
                    mark('already-ingested', True),
                    mark('stop', True),
                ]),
            ]),
            IF(is_marked('delete'), [
                update_old_object,
                delete_self_and_stop_processing
            ]),
            IF(is_marked('stop'), [
                stop_processing
            ]),
        ]),
        #
        # Article Processing
        # ==================
        IF(is_arxiv_paper, [
            arxiv_fulltext_download,
            arxiv_plot_extract,
            arxiv_refextract,
            arxiv_author_list("authorlist2marcxml.xsl"),
        ]),
        extract_journal_info,
        classify_paper(
            taxonomy="HEPont.rdf",
            only_core_tags=False,
            spires=True,
            with_author_keywords=True,
        ),
        filter_core_keywords,
        guess_categories,
        IF(is_experimental_paper, [
            guess_experiments,
        ]),
        guess_keywords,
        # Predict action for a generic HEP paper based only on title
        # and abstract.
        guess_coreness,  # ("arxiv_skip_astro_title_abstract.pickle)
        # Check if we shall halt or auto-reject
        # =====================================
        # NOTE: User submissions are always relevant
        IF_ELSE(is_record_relevant, [
            halt_record(action="hep_approval"),
        ], [
            reject_record("Article automatically rejected"),
            stop_processing
        ]),
        IF_ELSE(is_record_accepted, [
            IF(article_exists, [
                IF_ELSE(is_submission, [
                    reject_record('Article was already found on INSPIRE'),
                    stop_processing,
                    reply_ticket(
                        template="literaturesuggest/tickets/user_rejected_exists.html",
                        context_factory=reply_ticket_context
                    ),
                    close_ticket(ticket_id_key="ticket_id"),
                ], [
                    halt_record(action="merge_approval"),
                ]),
            ]),
            add_core,
            add_note_entry,
            filter_keywords,
            user_pdf_get,
            IF_ELSE(shall_push_remotely, [
                IF_ELSE(article_exists, [
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
                ])

            ], [
                store_record
            ]),
            IF(is_submission, [
                IF(curation_ticket_needed, [
                    create_ticket(
                        template="literaturesuggest/tickets/curation_core.html",
                        queue="HEP_curation",
                        context_factory=curation_ticket_context,
                        ticket_id_key="curation_ticket_id"
                    )
                ]),
                reply_ticket(
                    template="literaturesuggest/tickets/user_accepted.html",
                    context_factory=reply_ticket_context
                ),
            ]),
        ], [
            IF(is_submission, [
                reply_ticket(context_factory=reply_ticket_context)
            ])
        ]),
        close_ticket(ticket_id_key="ticket_id")
    ]
