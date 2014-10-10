# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
##
## In applying this license, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

"""Workflow for processing single arXiv records harvested."""

import collections
from six import string_types

from invenio.modules.workflows.tasks.marcxml_tasks import (
    convert_record_to_bibfield,
)

from inspire.modules.workflows.tasks.matching import(
    match_record_arxiv_remote_oaiharvest,
)

from invenio.modules.classifier.tasks.classification import (
    classify_paper_with_oaiharvester,
)

from invenio.modules.oaiharvester.tasks.postprocess import (
    convert_record_with_repository,
    plot_extract,
    arxiv_fulltext_download,
    refextract,
    author_list,
    upload_step,
)
from invenio.modules.workflows.tasks.workflows_tasks import log_info
from inspire.modules.workflows.tasks.actions import was_approved

from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio.modules.workflows.definitions import WorkflowBase
from ..tasks.filtering import inspire_filter_custom


class process_record_arxiv(WorkflowBase):

    """Processing workflow for a single arXiv record.

    The records have been harvested via oaiharvester.
    """

    object_type = "arXiv"

    workflow = [
        convert_record_with_repository("oaiarXiv2inspire_nofilter.xsl"),
        convert_record_to_bibfield,
        workflow_if(match_record_arxiv_remote_oaiharvest, True),
        [
            plot_extract(["latex"]),
            arxiv_fulltext_download,
            classify_paper_with_oaiharvester(
                taxonomy="HEPont",
                output_mode="dict",
            ),
            refextract,
            author_list,
            inspire_filter_custom(fields=["report_number", "arxiv_category"],
                                  custom_widgeted="*",
                                  custom_accepted="gr",
                                  action="inspire_approval"),
            workflow_if(was_approved),
            [
                upload_step,
            ],
            workflow_else,
            [
                log_info("Record rejected")
            ]
        ],
        workflow_else,
        [
            log_info("Record already into database"),
        ],
    ]

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
        except Exception:
            if hasattr(record, "get"):
                final_identifiers = [
                    record.get(
                        "system_number_external", {}
                    ).get("value", 'No ids')
                ]
            else:
                final_identifiers = [' No ids']

        task_results = bwo.get_tasks_results()
        results = []
        if 'bibclassify' in task_results:
            try:
                result = task_results['bibclassify'][0]['result']
                fast_mode = result.get('fast_mode', False)
                result = result['dict']['complete_output']
                result_string = "<strong></br>Bibclassify result:"\
                                "</br></strong>"\
                                "Number of Core keywords: \t%s</br>"\
                                "PACS: \t%s</br>"\
                                % (len(result['Core keywords']),
                                   len(result['Field codes']))
                if fast_mode:
                    result_string += "(This task run at fast mode"\
                                     " taking into consideration"\
                                     " only the title and the abstract)"
                results.append(result_string)
            except (KeyError, IndexError):
                pass
        categories = []
        if hasattr(record, "get"):
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

        from flask import render_template
        return render_template('workflows/styles/harvesting_record.html',
                               categories=categories,
                               identifiers=final_identifiers,
                               results=results)

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return a formatted version of the data."""
        from invenio.modules.formatter.engine import format_record

        data = bwo.get_data()
        if not data:
            return ''
        formatter = kwargs.get("formatter", None)
        format = kwargs.get("format", None)
        if formatter:
            # A seperate formatter is supplied
            return formatter(data)
        from invenio.modules.records.api import Record
        if isinstance(data, collections.Mapping):
            # Dicts are cool on its own, but maybe its SmartJson (record)
            try:
                data = Record(data.dumps()).legacy_export_as_marc()
            except (TypeError, KeyError):
                # Maybe not, submission?
                return data

        if isinstance(data, string_types):
            # Its a string type, lets try to convert
            if format:
                # We can try formatter!
                # If already XML, format_record does not like it.
                if format != 'xm':
                    try:
                        return format_record(recID=None,
                                             of=format,
                                             xml_record=data)
                    except TypeError:
                        # Wrong kind of type
                        pass
                else:
                    # So, XML then
                    from xml.dom.minidom import parseString

                    try:
                        pretty_data = parseString(data)
                        return pretty_data.toprettyxml()
                    except TypeError:
                        # Probably not proper XML string then
                        return "Data cannot be parsed: %s" % (data,)
                    except Exception:
                        # Some other parsing error
                        pass

            # Just return raw string
            return data
        if isinstance(data, set):
            return list(data)
        # Not any of the above types. How juicy!
        return data
