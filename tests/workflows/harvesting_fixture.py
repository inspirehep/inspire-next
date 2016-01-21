# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Implements a workflow for testing."""


from inspirehep.modules.converter.tasks import convert_record

from inspirehep.modules.oaiharvester.tasks.arxiv import (
    arxiv_plot_extract,
    arxiv_fulltext_download,
    arxiv_author_list,
    arxiv_refextract,
)

from inspirehep.modules.refextract.tasks import extract_journal_info


from inspirehep.modules.workflows.tasks.upload import (
    convert_record_to_json,
)
from inspirehep.modules.workflows.workflows.hep_ingestion import hep_ingestion


class harvesting_fixture(hep_ingestion):

    """A test workflow for the Payload class."""

    object_type = "test"

    initial_processing = [
        # First we perform conversion from OAI-PMH XML to MARCXML
        convert_record("oaiarXiv2inspire_nofilter.xsl"),
        # Then we convert from MARCXML to JSON object with doJSON
        convert_record_to_json,
    ] + hep_ingestion.initial_processing

    before_halt_check = [
        arxiv_plot_extract,
        arxiv_fulltext_download(),
        arxiv_refextract,
        arxiv_author_list("authorlist2marcxml.xsl"),
        extract_journal_info,
    ] + hep_ingestion.before_halt_check
