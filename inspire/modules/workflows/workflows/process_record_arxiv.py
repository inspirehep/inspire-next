# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

from flask import render_template

from invenio.modules.workflows.tasks.marcxml_tasks import (
    convert_record_to_bibfield,
)

from inspire.modules.workflows.tasks.matching import(
    match_record_arxiv_remote_oaiharvest,
    match_record_HP_oaiharvest,
    save_identifiers_oaiharvest,
    update_old_object,
    delete_self_and_stop_processing,
)

from inspire.modules.refextract.tasks import extract_journal_info

from invenio.modules.classifier.tasks.classification import (
    classify_paper_with_oaiharvester,
)

from invenio.modules.oaiharvester.tasks.postprocess import (
    convert_record_with_repository,
    plot_extract,
    arxiv_fulltext_download,
    refextract,
    author_list,
)
from invenio.modules.workflows.tasks.workflows_tasks import log_info
from inspire.modules.workflows.tasks.actions import (
    was_approved,
    add_core_oaiharvest,
)

from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio.modules.workflows.definitions import RecordWorkflow
from inspire.modules.oaiharvester.tasks.upload import (
    send_robotupload_oaiharvest,
)
from inspire.modules.workflows.tasks.submission import halt_record_with_action
from inspire.modules.classifier.tasks import (
    filter_core_keywords,
    guess_coreness
)


class process_record_arxiv(RecordWorkflow):

    """Processing workflow for a single arXiv record.

    The records have been harvested via oaiharvester.
    """

    object_type = "arXiv"

    workflow = [
        convert_record_with_repository("oaiarXiv2inspire_nofilter.xsl"),
        convert_record_to_bibfield(model=["hep"]),
        workflow_if(match_record_arxiv_remote_oaiharvest),
        [
            log_info("Record already into database"),
            delete_self_and_stop_processing,
            # update_existing_record_oaiharvest(),
        ],
        workflow_else,
        [
            workflow_if(match_record_HP_oaiharvest("HP_IDENTIFIERS")),
            [
                log_info("Record already into Holding Pen"),
                save_identifiers_oaiharvest("HP_IDENTIFIERS"),
                update_old_object("HP_IDENTIFIERS"),
                delete_self_and_stop_processing,
            ],
            workflow_else,
            [
                save_identifiers_oaiharvest("HP_IDENTIFIERS"),
                plot_extract(["latex"]),
                arxiv_fulltext_download,
                refextract,
                author_list,
                extract_journal_info,
                classify_paper_with_oaiharvester(
                    taxonomy="HEPont",
                    output_mode="dict",
                    only_core_tags=False,
                    spires=True,
                    with_author_keywords=True,
                ),
                filter_core_keywords(filter_kb="antihep"),
                guess_coreness(),
                halt_record_with_action(action="arxiv_approval",
                                        message="Accept article?"),
                workflow_if(was_approved),
                [
                    add_core_oaiharvest,
                    send_robotupload_oaiharvest(),
                ],
                workflow_else,
                [
                    log_info("Record rejected"),
                    delete_self_and_stop_processing,
                ],
            ],
        ],
    ]

    @staticmethod
    def get_description(bwo):
        """Get the description column part."""
        record = bwo.data
        abstract = ""
        authors = []
        categories = []
        final_identifiers = []
        if hasattr(record, "get"):
            # Get identifiers
            doi = record.get("doi")
            if doi:
                final_identifiers.append(doi)

            system_no = record.get("system_number_external", {}).get("value")
            if system_no:
                final_identifiers.append(system_no)

            # Get subject categories
            if 'subject' in record:
                lookup = ["subject", "term"]
            elif "subject_term":
                lookup = ["subject_term", "term"]
            else:
                lookup = None
            if lookup:
                primary, secondary = lookup
                category_list = record.get(primary, [])
                if isinstance(category_list, dict):
                    category_list = [category_list]
                for subject in category_list:
                    category = subject[secondary]
                    if len(subject) == 2:
                        if subject.keys()[1] == secondary:
                            source_list = subject[subject.keys()[0]]
                        else:
                            source_list = subject[subject.keys()[1]]
                    else:
                        try:
                            source_list = subject['source']
                        except KeyError:
                            source_list = ""
                    if source_list.lower() == 'inspire':
                        categories.append(category)
            abstract = record.get("abstract", {}).get("summary", "")
            authors = record.get("authors", [])
        return render_template('workflows/styles/harvesting_record.html',
                               object=bwo,
                               authors=authors,
                               categories=set(categories),
                               abstract=abstract,
                               identifiers=final_identifiers)

    @staticmethod
    def get_additional(bwo):
        from inspire.modules.classifier.utils import get_classification_from_task_results
        keywords = get_classification_from_task_results(bwo)
        results = bwo.get_tasks_results()
        core_guessing = results.get("core_guessing", {})
        if core_guessing:
            core_guessing = core_guessing[0].get("result")
        return render_template('workflows/styles/harvesting_record_additional.html',
                               object=bwo,
                               keywords=keywords,
                               top_words=core_guessing.get("top_words"),
                               core=core_guessing.get("core"),
                               overall_score=core_guessing.get("overall_score"))
