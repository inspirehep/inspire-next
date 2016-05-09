# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Main HEP literature submission workflow."""

from __future__ import absolute_import, print_function

from flask import render_template

from six import string_types

from invenio_records.api import Record

from workflow.patterns.controlflow import IF, IF_ELSE

from inspirehep.dojson.hep import hep2marc
from inspirehep.utils.record import get_value

from inspirehep.modules.workflows.tasks.actions import (
    reject_record,
    add_core,
    shall_push_remotely,
    halt_record,
    shall_upload_record
)
from inspirehep.modules.workflows.tasks.classifier import classify_paper
from inspirehep.modules.workflows.tasks.matching import match_legacy_inspire
from inspirehep.modules.workflows.tasks.submission import (
    send_robotupload,
    create_ticket,
    reply_ticket,
    add_note_entry,
    user_pdf_get,
    close_ticket,
)
from inspirehep.modules.workflows.tasks.upload import store_record
# from inspirehep.modules.predicter.tasks import guess_coreness

from ..forms import LiteratureForm
from ..tasks import (
    curation_ticket_needed,
    reply_ticket_context,
    new_ticket_context,
    curation_ticket_context,
    convert_data_to_model
)


class Literature(object):
    """Literature deposit submission."""

    name = "Literature Suggestion"
    data_type = "hep"

    workflow = [
        create_ticket(template="literaturesuggest/tickets/curator_submitted.html",
                      queue="HEP_add_user",
                      context_factory=new_ticket_context,
                      ticket_id_key="ticket_id"),
        reply_ticket(template="literaturesuggest/tickets/user_submitted.html",
                     context_factory=reply_ticket_context,
                     keep_new=True),
        # guess_coreness("literature_guessing.pickle"),
        classify_paper(taxonomy="HEPont.rdf"),
        halt_record(action="core_approval",
                    message="Accept submission?"),
        IF_ELSE(shall_upload_record, [
            IF_ELSE(match_legacy_inspire, [
                reject_record('Record was already found on INSPIRE'),
                reply_ticket(
                    template="literaturesuggest/tickets/user_rejected_exists.html",
                    context_factory=reply_ticket_context
                ),
            ], [
                add_core,
                add_note_entry,
                user_pdf_get,
                IF_ELSE(shall_push_remotely, [
                    send_robotupload(marcxml_processor=hep2marc),
                ], [
                    store_record
                ]),
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
            ])
        ], [
            reply_ticket(context_factory=reply_ticket_context)
        ]),
        close_ticket(ticket_id_key="ticket_id")
    ]

    @classmethod
    def get_title(cls, obj, **kwargs):
        """Return the value to put in the title column of Holding Pen."""
        if isinstance(obj.data, dict):
            titles = filter(None, get_value(obj.data, "titles.title", []))
            if titles:
                # Show first title that evaluates to True
                return titles[0]
        return "No title available"

    @classmethod
    def get_additional(cls, obj, **kwargs):
        """Return the value to put in the additional column of HoldingPen."""
        keywords = obj.extra_data.get('classifier_results', {}).get(
            "complete_output"
        )
        results = obj.extra_data.get('_tasks_results', {})
        prediction_results = results.get("arxiv_guessing", {})
        if prediction_results:
            prediction_results = prediction_results[0].get("result")
        return render_template(
            'inspire_workflows/styles/harvesting_record_additional.html',
            object=obj,
            keywords=keywords,
            score=prediction_results.get("max_score"),
            decision=prediction_results.get("decision")
        )

    @classmethod
    def formatter(cls, obj, **kwargs):
        """Nicely format the record."""
        if not obj.data:
            return ""
        if kwargs and kwargs.get('of') == 'xm':
            from inspirehep.dojson.utils import legacy_export_as_marc
            return legacy_export_as_marc(hep2marc.do(obj.data))
        return render_template(
            'inspirehep_theme/format/record/Holding_Pen_HTML_detailed.tpl',
            record=obj.data
        )

    @classmethod
    def get_sort_data(cls, obj, **kwargs):
        """Return a dictionary useful for sorting in Holding Pen."""
        results = obj.extra_data.get("_tasks_results", {})
        prediction_results = results.get("arxiv_guessing", {})
        if prediction_results:
            prediction_results = prediction_results[0].get("result")
            max_score = prediction_results.get("max_score")
            decision = prediction_results.get("decision")
            relevance_score = max_score
            if decision == "CORE":
                relevance_score += 10
            elif decision == "Rejected":
                relevance_score = (max_score * -1) - 10
            return {
                "max_score": prediction_results.get("max_score"),
                "decision": prediction_results.get("decision"),
                "relevance_score": relevance_score
            }
        else:
            return {}

    @classmethod
    def get_record(cls, obj, **kwargs):
        """Return a dictionary-like object representing the current object.

        This object will be used for indexing and be the basis for display
        in Holding Pen.
        """
        if not isinstance(obj.data, dict):
            return {}
        return obj.data

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        from invenio_accounts.models import User

        try:
            email = User.query.get(bwo.id_user).email
        except AttributeError:
            email = ''

        data = bwo.data
        if data:
            record = Record(data)
            identifiers = []
            report_numbers = record.get("report_numbers", [])
            dois = record.get("dois.value", [])
            if report_numbers:
                for report_number in report_numbers:
                    number = report_number.get("value", "")
                    if number:
                        identifiers.append(number)
            if dois:
                identifiers.extend(["doi:{0}".format(d) for d in dois])

            categories = []
            subjects = record.get("subject_terms", [])
            if subjects:
                for subject in subjects:
                    if isinstance(subject, string_types):
                        categories.append(subject)
                    elif isinstance(subject, dict):
                        if subject.get("term"):
                            categories.append(subject.get("term"))
            categories = [record.get("type_of_doc", "")] + categories

            authors = []
            authors += [record.get("_first_author", {})]
            authors += record.get("_additional_authors", [])
            return render_template(
                'literaturesuggest/workflows/submission_record.html',
                categories=categories,
                authors=authors,
                identifiers=identifiers,
                # results=results,
                user_email=email,
                object=bwo,
                record=record
            )
        else:
            return "Submitter: {0}".format(email)
