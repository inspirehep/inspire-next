# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

import re

from flask import render_template

from invenio.modules.deposit.types import SimpleRecordDeposition
from invenio.modules.deposit.tasks import render_form, \
    prepare_sip, \
    finalize_record_sip, \
    prefill_draft, \
    process_sip_metadata

from ..tasks import arxiv_fft_get

from inspire.modules.deposit.forms import LiteratureForm
from invenio.modules.deposit.models import Deposition

from invenio.modules.classifier.tasks.classification import (
    classify_paper_with_deposit,
)

from inspire.modules.workflows.tasks.submission import (
    halt_record_with_action,
    send_robotupload,
    halt_to_render,
    inform_submitter,
    add_files_to_task_results,
)

from inspire.modules.workflows.tasks.actions import was_approved
from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if
)
from invenio.modules.workflows.definitions import WorkflowBase


class literature(SimpleRecordDeposition, WorkflowBase):

    """Literature deposit submission."""

    object_type = "submission"

    workflow = [
        # Pre-fill draft with values passed in from request
        prefill_draft(draft_id='default'),
        # Render form and wait for user to submit
        render_form(draft_id='default'),
        # Create the submission information package by merging form data
        # from all drafts (in this case only one draft exists).
        prepare_sip(),
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        # Get FFT from arXiv, if arXiv ID is provided
        arxiv_fft_get,
        add_files_to_task_results,
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(is_dump=False),
        halt_to_render,
        classify_paper_with_deposit(
            taxonomy="HEPont.rdf",
            output_mode="dict",
        ),
        halt_record_with_action(action="inspire_approval",
                                message="Accept submission?"),
        workflow_if(was_approved),
        [
            send_robotupload()
        ],
        inform_submitter
    ]

    name = "Literature"
    name_plural = "Literature submissions"
    group = "Articles & Preprints"
    draft_definitions = {
        'default': LiteratureForm,
    }

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        deposit_object = Deposition(bwo)
        sip = deposit_object.get_latest_sip()
        if sip:
            # Get the SmartJSON object
            record = sip.metadata
            return record.get("title", {"title": "No title"}).get("title")
        else:
            return "User submission in progress!!"

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        deposit_object = Deposition(bwo)
        sip = deposit_object.get_latest_sip()
        if sip:
            record = sip.metadata
            identifiers = [record.get("arxiv_id", "")]
            categories = [record.get("type_of_doc", "")]
            return render_template('workflows/styles/submission_record.html',
                                   categories=categories,
                                   identifiers=identifiers)
        else:
            from invenio.modules.access.control import acc_get_user_email
            id_user = deposit_object.workflow_object.id_user
            return "Submitted by: %s" % str(acc_get_user_email(id_user))

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        from invenio.modules.formatter.engine import format_record
        deposit_object = Deposition(bwo)
        submission_data = deposit_object.get_latest_sip()
        marcxml = submission_data.package

        of = kwargs.get("format", "hd")
        if of == "xm":
            return marcxml
        else:
            return format_record(
                recID=None,
                of=kwargs.get("format", "hd"),
                xml_record=marcxml
            )

    @classmethod
    #TODO: ensure that this regex is correct
    def match_authors_initials(self, author_name):
        """Check if author's name contains only its initials."""
        return not bool(re.compile(r'[^A-Z. ]').search(author_name))

    @classmethod
    def process_sip_metadata(cls, deposition, metadata):
        """Map fields to match jsonalchemy configuration."""
        delete_keys = []
        field_list = ['abstract', 'title']

        # maps from a form field to the corresponding MarcXML field
        field_map = {'abstract': "summary",
                     'title': "title",
                     'subject_term': "term",
                     'defense_date': "date",
                     'university': "university",
                     'degree_type': "degree_type",
                     'journal_title': "journal_title",
                     'page_range': "page_artid",
                     'article_id': "page_artid",
                     'volume': "journal_volume",
                     'year': "year",
                     'issue': "journal_issue"}

        # ============================
        # Abstract, Title and Subjects
        # ============================
        for field in field_list:
            if field in metadata:
                tmp_field = metadata[field]
                metadata[field] = {}
                metadata[field][field_map[field]] = tmp_field

        if "subject_term" in metadata:
            tmp_field = metadata["subject_term"]
            metadata["subject_term"] = [{"term": t, "scheme": "INSPIRE"}
                                        for t in tmp_field]

        # =======
        # Authors
        # =======
        metadata['authors'] = filter(None, metadata['authors'])
        if 'authors' in metadata and metadata['authors']:
            first_author = metadata['authors'][0].get('full_name').split(',')
            if len(first_author) > 1 and \
                    literature.match_authors_initials(first_author[1]):
                first_author[1] = first_author[1].replace(' ', '')
                metadata['authors'][0]['full_name'] = ",".join(first_author)
            metadata['_first_author'] = metadata['authors'][0]
            metadata['_first_author']['email'] = ''
            if metadata['authors'][1:]:
                metadata['_additional_authors'] = metadata['authors'][1:]
                for k in metadata['_additional_authors']:
                    try:
                        additional_author = k.get('full_name').split(',')
                        if len(additional_author) > 1 and \
                                literature.match_authors_initials(additional_author[1]):
                            additional_author[1] = additional_author[1].replace(' ', '')
                            k['full_name'] = ",".join(additional_author)
                        k['email'] = ''
                    except AttributeError:
                        pass
            delete_keys.append('authors')

        # ===========
        # Supervisors
        # ===========
        if 'supervisors' in metadata and metadata['supervisors']:
            metadata['thesis_supervisor'] = metadata['supervisors'][0]
            metadata['thesis_supervisor']['email'] = ''
            #metadata['_additional_authors'] = metadata['authors'][1:]
            delete_keys.append('supervisors')

        # ==============
        # Thesis related
        # ==============
        thesis_fields = filter(lambda field: field in metadata, ['defense_date',
                                                                 'university',
                                                                 'degree_type'])
        if thesis_fields:
            metadata['thesis'] = {}

            for field in thesis_fields:
                metadata['thesis'][field_map[field]] = metadata[field]

            delete_keys.extend(thesis_fields)

        # ========
        # Category
        # ========
        metadata['collections'] = [{'primary': "HEP"}]

        # ===============
        # Abstract source
        # ===============
        if 'title_arXiv' in metadata:
            metadata['abstract']['source'] = 'arXiv'

        # ========
        # arXiv ID
        # ========
        if 'arxiv_id' in metadata:
            metadata['report_number'] = "$$9arXiv$$aoai:arXiv.org:" + metadata['arxiv_id']

        # ========
        # Language
        # ========
        metadata['language'] = unicode(dict(LiteratureForm.languages).get(metadata['language']))

        # ==========
        # Experiment
        # ==========
        if 'experiment' in metadata:
            metadata['accelerator_experiment'] = {}
            metadata['accelerator_experiment']['experiment'] = metadata['experiment']
            delete_keys.append('experiment')

        # ===============
        # Conference Info
        # ===============
        if 'conf_name' in metadata:
            if 'nonpublic_note' in metadata:
                field = [metadata['nonpublic_note'], metadata['conf_name']]
                metadata['nonpublic_note'] = field
            else:
                metadata['nonpublic_note'] = [metadata['conf_name']]
            metadata['collections'].extend([{'primary': "ConferencePaper"}])
            delete_keys.append('conf_name')

        # =======
        # License
        # =======
        if 'license_url' in metadata:
            metadata['license'] = {}
            metadata['license']['url'] = metadata['license_url']
            delete_keys.append('license_url')

        # ===========
        # Files (FFT)
        # ===========
        if 'fft' in metadata and metadata['fft']:
            fft = metadata['fft']
            metadata['fft'] = {}
            metadata['fft']['url'] = fft[0]['path']

        # ================
        # Publication Info
        # ================
        publication_fields = filter(lambda field: field in metadata, ['journal_title',
                                                                      'page_range',
                                                                      'article_id',
                                                                      'volume',
                                                                      'year',
                                                                      'issue'])
        if publication_fields:
            metadata['publication_info'] = {}

            for field in publication_fields:
                metadata['publication_info'][field_map[field]] = metadata[field]

            if 'page_nr' not in metadata and 'page_range' in publication_fields:
                pages = metadata['page_range'].split('-')
                if len(pages) == 2:
                    try:
                        metadata['page_nr'] = int(pages[1])-int(pages[0])
                    except ValueError:
                        pass

            delete_keys.extend(publication_fields)

            if 'nonpublic_note' in metadata and len(metadata['nonpublic_note']) > 1:
                del metadata['nonpublic_note'][0]

            if {'primary': "ConferencePaper"} in metadata['collections']:
                metadata['collections'].remove({'primary': "ConferencePaper"})
            metadata['collections'].append({'primary': "Published"})

        # ===================
        # Delete useless data
        # ===================
        for key in delete_keys:
            del metadata[key]
