# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013, 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from invenio.modules.workflows.tasks.marcxml_tasks import (
    convert_record_with_repository,
    convert_record_to_bibfield,
    plot_extract,
    fulltext_download,
    refextract,
    author_list,
    upload_step,
    quick_match_record,
    bibclassify,
)

from invenio.modules.workflows.tasks.workflows_tasks import log_info

from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)

from ..tasks.filtering import inspire_filter_custom

from invenio.config import CFG_PREFIX


class process_record_arxiv(object):
    object_type = "record"
    workflow = [
        convert_record_with_repository("oaiarXiv2inspire_nofilter.xsl"), convert_record_to_bibfield,
        workflow_if(quick_match_record, True),
        [
            plot_extract(["latex"]),
            fulltext_download,
            inspire_filter_custom(fields=["report_number", "arxiv_category"],
                                  custom_widgeted="*",
                                  action="inspire_approval"),
            bibclassify(taxonomy=CFG_PREFIX + "/etc/bibclassify/HEP.rdf",
                        output_mode="dict",
                        match_mode="partial"),
            refextract, author_list,
            upload_step,
        ],
        workflow_else,
        [
            log_info("Record already into database"),
        ],
    ]
