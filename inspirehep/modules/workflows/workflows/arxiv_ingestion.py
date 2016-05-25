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

from inspirehep.modules.workflows.tasks.arxiv import (
    arxiv_author_list,
    arxiv_fulltext_download,
    arxiv_plot_extract,
    arxiv_refextract,
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
from inspirehep.modules.refextract.tasks import extract_journal_info

from inspirehep.modules.workflows.tasks.beard import (
    guess_coreness,
)

from .hep_ingestion import HEPIngestion


class ArXivIngestion(HEPIngestion):
    """Processing workflow for a single arXiv record.

    The records have been harvested via oaiharvester.
    """
    name = "arXiv"

    # Need staticmethod here to avoid needing class instances
    upload_check = staticmethod(shall_upload_record)

    match_processing = [
        # FIXME: This filtering step should be removed when
        #        arXiv CORE harvesting is enabled on labs
        IF(already_harvested, [
            delete_self_and_stop_processing,
        ]),
        # FIXME: This filtering step should be removed when:
        #        old previously rejected records are treated differently
        #        e.g. good auto-reject heuristics or better time based
        #        filtering (5 days is quite random now.
        IF(previously_rejected(), [
            delete_self_and_stop_processing,
        ]),
    ] + HEPIngestion.match_processing

    before_halt_check = [
        arxiv_plot_extract,
        arxiv_fulltext_download(),
        arxiv_refextract,
        arxiv_author_list("authorlist2marcxml.xsl"),
        extract_journal_info,
        classify_paper(
            taxonomy="HEPont.rdf",
            only_core_tags=False,
            spires=True,
            with_author_keywords=True,
        ),
        filter_core_keywords,
        # Predict action for a generic HEP paper based only on title
        # and abstract.
        guess_coreness,   # ("new_astro_model.pickle", top_words=10)
    ]
