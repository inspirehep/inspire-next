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


class process_record_arxiv(WorkflowBase):
    @staticmethod
    def get_title(bwo):
        """Get the title."""
        extracted_title = []
        record = bwo.get_data()
        if hasattr(record, "get") and "title" in record:
            if isinstance(record["title"], str):
                extracted_title = [record["title"]]
            else:
                for a_title in record["title"]:
                    extracted_title.append(record["title"][a_title])
        else:
            extracted_title = [" No title"]
        title_final = ""
        for i in extracted_title:
            title_final += "{0} ".format(i)
        return title_final

    @staticmethod
    def get_description(bwo):
        """Get the description column part."""
        record = bwo.get_data()
        from invenio.modules.records.api import Record

        try:
            identifiers = Record(record.dumps()).persistent_identifiers
            final_identifiers = []
            for i in identifiers:
                final_identifiers.append(i['value'])
        except Exception as e:
            if hasattr(record, "get"):
                final_identifiers = [record.get("system_number_external", {}).get("value", 'No ids')]
            else:
                final_identifiers = [' No ids']

        categories = [" No categories"]
        if hasattr(record, "get"):
            if 'subject' in record:
                lookup = ["subject", "term"]
            elif "subject_term":
                lookup = ["subject_term", "term"]
            else:
                lookup = None
            categories = []
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
                    categories.append(category + "(" + source_list + ")")

        from flask import render_template
        return render_template('workflows/styles/harvesting_record.html',
                               categories=categories,
                               identifiers=final_identifiers)
    @staticmethod
    def formatter(bwo, **kwargs):
        return None

    object_type = "record"
    workflow = [
        convert_record_with_repository("oaiarXiv2inspire_nofilter.xsl"), convert_record_to_bibfield,
        workflow_if(quick_match_record, True),
        [
            plot_extract(["latex"]),
            fulltext_download,
            inspire_filter_custom(fields=["report_number", "arxiv_category"],
                                  custom_widgeted="*",
                                  custom_accepted="gr",
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
