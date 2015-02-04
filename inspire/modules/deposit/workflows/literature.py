# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
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

from six import string_types

from invenio.base.globals import cfg
from invenio.ext.login import UserInfo
from invenio.modules.accounts.models import UserEXT

from invenio.modules.deposit.types import SimpleRecordDeposition
from invenio.modules.deposit.tasks import render_form, \
    prepare_sip, \
    finalize_record_sip, \
    prefill_draft, \
    process_sip_metadata
from invenio.modules.deposit.models import Deposition, InvalidDepositionType
from invenio.modules.classifier.tasks.classification import (
    classify_paper_with_deposit,
)
from invenio.modules.knowledge.api import get_kb_mappings
from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio.modules.workflows.definitions import WorkflowBase

from invenio.utils.persistentid import is_arxiv_post_2007

from inspire.modules.workflows.tasks.matching import(
    match_record_remote_deposit,
)
from inspire.modules.workflows.tasks.submission import (
    halt_record_with_action,
    send_robotupload_deposit,
    halt_to_render,
    add_files_to_task_results,
    create_ticket,
    reply_ticket,
    close_ticket
)
from inspire.modules.workflows.tasks.actions import (
    was_approved,
    reject_record,
    add_core_deposit
)
from inspire.modules.deposit.forms import LiteratureForm

from ..tasks import add_submission_extra_data
from ..utils import filter_empty_helper


def filter_empty_elements(recjson):
    """Filter empty fields."""
    list_fields = [
        'authors', 'supervisors', 'report_numbers'
    ]
    for key in list_fields:
        recjson[key] = filter(
            filter_empty_helper(), recjson.get(key, [])
        )

    return recjson


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
        add_submission_extra_data,
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(is_dump=False),
        halt_to_render,
        create_ticket(template="deposit/tickets/curator_submitted.html",
                      queue="HEP_add_user",
                      ticket_id_key="ticket_id"),
        reply_ticket(template="deposit/tickets/user_submitted.html",
                     keep_new=True),
        add_files_to_task_results,
        classify_paper_with_deposit(
            taxonomy="HEPont.rdf",
            output_mode="dict",
        ),
        halt_record_with_action(action="core_approval",
                                message="Accept submission?"),
        workflow_if(was_approved),
        [
            workflow_if(match_record_remote_deposit, True),
            [
                add_core_deposit,
                finalize_record_sip(is_dump=False),
                send_robotupload_deposit(),
                reply_ticket(template="deposit/tickets/user_accepted.html"),
            ],
            workflow_else,
            [
                reject_record('Record was already found on INSPIRE'),
                reply_ticket(template="deposit/tickets/user_rejected_exists.html"),
            ],
        ],
        workflow_else,
        [
            reply_ticket()  # setting template=None as text come from Holding Pen
        ],
        close_ticket(ticket_id_key="ticket_id")
    ]

    name = "Literature"
    name_plural = "Suggest content"
    group = "Articles & Preprints"
    draft_definitions = {
        'default': LiteratureForm,
    }

    @staticmethod
    def get_title(bwo):
        """Return title of object."""
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)
        sip = deposit_object.get_latest_sip()
        if sip:
            # Get the SmartJSON object
            record = sip.metadata
            try:
                return record.get("title", {"title": "No title"}).get("title")
            except AttributeError:
                return record.get("title")
        else:
            return "User submission in progress"

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        from invenio.modules.access.control import acc_get_user_email
        results = bwo.get_tasks_results()
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)

        id_user = deposit_object.workflow_object.id_user
        user_email = acc_get_user_email(id_user)

        sip = deposit_object.get_latest_sip()
        if sip:
            record = sip.metadata
            identifiers = [record.get("arxiv_id", "")]
            categories = [record.get("type_of_doc", "")]
            return render_template('workflows/styles/submission_record.html',
                                   categories=categories,
                                   identifiers=identifiers,
                                   results=results,
                                   user_email=user_email,
                                   )
        else:
            return "Submitter: {0}".format(user_email)

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        from invenio.modules.formatter import format_record
        try:
            deposit_object = Deposition(bwo)
        except InvalidDepositionType:
            return "This submission is disabled: {0}.".format(bwo.workflow.name)

        submission_data = deposit_object.get_latest_sip(deposit_object.submitted)

        if hasattr(submission_data, "package"):
            marcxml = submission_data.package
        else:
            return "No data found in submission (no package)."

        of = kwargs.get("of", "hd")
        if of == "xm":
            return marcxml
        else:
            return format_record(
                recID=None,
                of=of,
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
                     'institution': "university",
                     'degree_type': 'degree_type',
                     'thesis_date': "date",
                     'journal_title': "journal_title",
                     'page_range_article_id': "page_artid",
                     'volume': "journal_volume",
                     'year': "year",
                     'issue': "journal_issue",
                     'conference_id': "cnum"}

        # exclusive fields for each type of document
        doc_exclusive_fields = {'article': ['journal_title',
                                            'page_range',
                                            'article_id',
                                            'volume',
                                            'year',
                                            'issue',
                                            'conference_id'],
                                'thesis': ['supervisors',
                                           'institution',
                                           'degree_type',
                                           'thesis_date',
                                           'defense_date'],
                                }

        del doc_exclusive_fields[metadata['type_of_doc']]

        def remove_exclusive_fields(fieldlist):
            for field in fieldlist:
                if field in metadata and metadata[field]:
                    del metadata[field]

        map(remove_exclusive_fields, doc_exclusive_fields.values())

        filter_empty_elements(metadata)

        # ============================
        # Abstract, Title and Subjects
        # ============================
        for field in field_list:
            if field in metadata:
                tmp_field = metadata[field]
                metadata[field] = {field_map[field]: tmp_field}

        if "subject_term" in metadata:
            tmp_field = metadata["subject_term"]
            metadata["subject_term"] = [{"term": t,
                                        "scheme": "INSPIRE",
                                        "source": "submitter"}
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
                metadata['authors'][0]['full_name'] = ", ".join(first_author)
            metadata['_first_author'] = metadata['authors'][0]
            if metadata['authors'][1:]:
                metadata['_additional_authors'] = metadata['authors'][1:]
                for k in metadata['_additional_authors']:
                    try:
                        additional_author = k.get('full_name').split(',')
                        if len(additional_author) > 1 and \
                                literature.match_authors_initials(additional_author[1]):
                            additional_author[1] = additional_author[1].replace(' ', '')
                            k['full_name'] = ", ".join(additional_author)
                    except AttributeError:
                        pass
            delete_keys.append('authors')

        # ===========
        # Supervisors
        # ===========
        if 'supervisors' in metadata and metadata['supervisors']:
            metadata['thesis_supervisor'] = metadata['supervisors']
            delete_keys.append('supervisors')

        # ==============
        # Thesis related
        # ==============
        thesis_fields = filter(lambda field: field in metadata, ['institution',
                                                                 'degree_type',
                                                                 'thesis_date'])
        if thesis_fields:
            metadata['thesis'] = {}

            for field in thesis_fields:
                metadata['thesis'][field_map[field]] = metadata[field]

            delete_keys.extend(thesis_fields)

        if 'defense_date' in metadata and metadata['defense_date']:
            if 'note' in metadata and metadata['note']:
                metadata['note'] += ', presented on ' + metadata['defense_date']
            else:
                metadata['note'] = 'Presented on ' + metadata['defense_date']

        # ========
        # Category
        # ========
        metadata['collections'] = [{'primary': "HEP"}]
        if metadata['type_of_doc'] == 'thesis':
            metadata['collections'].append({'primary': "THESIS"})

        # ============
        # Title source
        # ============
        if 'title_source' in metadata and metadata['title_source']:
            metadata['title']['source'] = metadata['title_source']
            delete_keys.append('title_source')

        # =============
        # Report number
        # =============
        user_report_number = None
        if 'report_numbers' in metadata and metadata['report_numbers']:
            user_report_number = metadata['report_numbers']
            delete_keys.append('report_numbers')

        # ========
        # arXiv ID
        # ========
        imported_from_arXiv = filter(lambda field: field in metadata,
                                     ['categories', 'title_arXiv'])

        if imported_from_arXiv or metadata.get('title_source') == 'arXiv':
            if is_arxiv_post_2007(metadata['arxiv_id']):
                metadata['report_number'] = {'primary': 'arXiv:' + metadata['arxiv_id'],
                                             'source': 'arXiv'}
            else:
                metadata['report_number'] = {'primary': metadata['arxiv_id'],
                                             'source': 'arXiv'}
            if len(metadata['arxiv_id'].split('/')) == 2:
                metadata['report_number']['arxiv_category'] = metadata['arxiv_id'].split('/')[0]
            if 'abstract' in metadata:
                metadata['abstract']['source'] = 'arXiv'
            if 'title_arXiv' in metadata:
                title_arXiv = metadata['title_arXiv']
                metadata['title_arXiv'] = {}
                metadata['title_arXiv']['value'] = title_arXiv
                metadata['title_arXiv']['source'] = 'arXiv'
            if 'categories' in metadata and metadata['categories']:
                # arXiv subject categories
                subject_list = [{"term": c, "scheme": "arXiv"}
                                for c in metadata['categories'].split()]
                # INSPIRE subject categories
                if 'subject_term' in metadata and metadata['subject_term']:
                    metadata['subject_term'].extend(subject_list)
                else:
                    metadata['subject_term'] = subject_list
            metadata['system_number_external'] = {'value': 'oai:arXiv.org:' + metadata['arxiv_id'],
                                                  'institute': 'arXiv'}
            metadata['collections'].extend([{'primary': "arXiv"}, {'primary': "Citeable"}])

        if user_report_number:
            metadata['report_number'] = [{'primary': v['report_number']}
                                         for v in user_report_number]

        # ========
        # Language
        # ========
        if metadata['language'] not in ('en', 'oth'):
            metadata['language'] = unicode(dict(LiteratureForm.languages).get(metadata['language']))
        elif metadata['language'] == 'oth':
            if metadata['other_language']:
                metadata['language'] = metadata['other_language']
        else:
            delete_keys.append('language')

        # ==========
        # Experiment
        # ==========
        if 'experiment' in metadata:
            metadata['accelerator_experiment'] = {'experiment': metadata['experiment']}
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
        licenses_kb = dict([(x['key'], x['value'])
            for x in get_kb_mappings(cfg["DEPOSIT_INSPIRE_LICENSE_KB"])])
        if 'license' in metadata and metadata['license']:
            metadata['license'] = {'license': metadata['license']}
            if 'license_url' in metadata:
                metadata['license']['url'] = metadata['license_url']
            else:
                metadata['license']['url'] = licenses_kb.get(
                    metadata['license']['license'])
        elif 'license_url' in metadata:
            metadata['license'] = {'url': metadata['license_url']}
            license_key = {v: k for k, v in licenses_kb.items()}.get(
                metadata['license_url'])
            if license_key:
                metadata['license']['license'] = license_key
            delete_keys.append('license_url')

        # ===========
        # Files (FFT)
        # ===========
        if 'fft' in metadata and metadata['fft']:
            def restructure_ffts(fft):
                fft['url'] = fft['path']
                fft['description'] = fft['name']
                fft['docfile_type'] = "INSPIRE-PUBLIC"
                del fft['path'], fft['name']

            map(restructure_ffts, metadata['fft'])

        # ====
        # URLs
        # ====
        if metadata.get('url'):
            metadata['pdf'] = metadata['url']
            if isinstance(metadata['url'], string_types):
                metadata['url'] = [{'url': metadata['url']}]
        if 'additional_url' in metadata and metadata['additional_url']:
            if metadata.get('url'):
                metadata['url'].append({'url': metadata['additional_url']})
            else:
                metadata['url'] = [{'url': metadata['additional_url']}]
            delete_keys.append('additional_url')

        # ================
        # Publication Info
        # ================

        publication_fields = filter(lambda field: field in metadata, ['journal_title',
                                                                      'page_range_article_id',
                                                                      'volume',
                                                                      'year',
                                                                      'issue',
                                                                      'conference_id'])
        if publication_fields:
            metadata['publication_info'] = {}

            for field in publication_fields:
                metadata['publication_info'][field_map[field]] = metadata[field]

            if 'page_nr' not in metadata and 'page_range_article_id' in publication_fields:
                pages = metadata['page_range_article_id'].split('-')
                if len(pages) == 2:
                    try:
                        metadata['page_nr'] = int(pages[1]) - int(pages[0]) + 1
                    except ValueError:
                        pass

            if {'primary': "ConferencePaper"} not in metadata['collections']:
                metadata['collections'].append({'primary': "Published"})

            delete_keys.extend(publication_fields)

        if 'journal_title' in metadata:
            journals_kb = dict([(x['key'].lower(), x['value'])
                                for x in get_kb_mappings(cfg.get("DEPOSIT_INSPIRE_JOURNALS_KB"))])

            metadata['publication_info']['journal_title'] = journals_kb.get(metadata['journal_title'].lower(),
                                                                            metadata['journal_title'])

            if 'nonpublic_note' in metadata:
                if (isinstance(metadata['nonpublic_note'], list)
                        and len(metadata['nonpublic_note']) > 1):
                    del metadata['nonpublic_note'][0]
                else:
                    delete_keys.append('nonpublic_note')

        # =============
        # Preprint Info
        # =============
        if 'created' in metadata and metadata['created']:
            metadata['preprint_info'] = {'date': metadata['created']}
            delete_keys.append('created')

        # ==========
        # Owner Info
        # ==========
        userid = deposition.user_id
        user = UserInfo(userid)
        email = user.info.get('email', '')
        external_ids = UserEXT.query.filter_by(id_user=userid).all()
        sources = ["{0}{1}".format('inspire:uid:', userid)]
        sources.extend(["{0}:{1}".format(e_id.method,
                                         e_id.id) for e_id in external_ids])
        metadata['acquisition_source'] = dict(
            source=sources,
            email=email,
            method="submission",
            submission_number=deposition.id,
        )

        # ==============
        # Extra comments
        # ==============
        if 'extra_comments' in metadata and metadata['extra_comments']:
            metadata['hidden_note'] = {'value': metadata['extra_comments'],
                                       'source': 'submitter'}

        # ===================
        # Delete useless data
        # ===================
        for key in delete_keys:
            del metadata[key]
