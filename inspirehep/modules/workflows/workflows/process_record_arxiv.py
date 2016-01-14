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

from inspirehep.modules.converter.tasks import convert_record
from inspirehep.modules.oaiharvester.tasks.arxiv import (
    arxiv_author_list,
    arxiv_fulltext_download,
    arxiv_plot_extract,
)
from inspirehep.modules.predicter.tasks import (
    guess_coreness,
)
from inspirehep.modules.workflows.tasks.matching import(
    delete_self_and_stop_processing,
    already_harvested,
    previously_rejected,
)
from inspirehep.modules.workflows.tasks.actions import shall_upload_record
from inspirehep.modules.workflows.tasks.classifier import (
    classify_paper,
    filter_core_keywords,
)
from inspirehep.modules.workflows.workflows.hep_ingestion import hep_ingestion

from invenio_oaiharvester.tasks.records import convert_record_to_json
from invenio_workflows.tasks.logic_tasks import workflow_if
# from inspirehep.modules.refextract.tasks import extract_journal_info


class process_record_arxiv(hep_ingestion):

    """Processing workflow for a single arXiv record.

    The records have been harvested via oaiharvester.
    """

    object_type = "arXiv"

    # Need staticmethod here to avoid needing class instances
    upload_check = staticmethod(shall_upload_record)

    match_processing = [
        # FIXME: This filtering step should be removed when
        #        arXiv CORE harvesting is enabled on labs
        workflow_if(already_harvested),
        [
            delete_self_and_stop_processing,
        ],
        # FIXME: This filtering step should be removed when:
        #        old previously rejected records are treated differently
        #        e.g. good auto-reject heuristics or better time based
        #        filtering (5 days is quite random now.
        workflow_if(previously_rejected()),
        [
            delete_self_and_stop_processing,
        ]
    ] + hep_ingestion.match_processing

    initial_processing = [
        # First we perform conversion from OAI-PMH XML to MARCXML
        convert_record("oaiarXiv2inspire_nofilter.xsl"),
        # Then we convert from MARCXML to JSON object with doJSON
        convert_record_to_json,
    ] + hep_ingestion.initial_processing

    before_halt_check = [
        arxiv_plot_extract,
        arxiv_fulltext_download(),
        # arxiv_refextract,
        arxiv_author_list("authorlist2marcxml.xsl"),
        # extract_journal_info,
        classify_paper(
            taxonomy="HEPont",
            only_core_tags=False,
            spires=True,
            with_author_keywords=True,
        ),
        filter_core_keywords(filter_kb="antihep"),
        # Predict action for a generic HEP paper based only on title
        # and abstract.
        guess_coreness("new_astro_model.pickle")
    ]
