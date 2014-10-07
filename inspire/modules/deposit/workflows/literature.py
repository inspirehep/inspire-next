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
from invenio.ext.login import UserInfo
from invenio.modules.oauthclient.models import RemoteAccount

from ..tasks import arxiv_fft_get, add_submission_extra_data

from inspire.modules.deposit.forms import LiteratureForm
from invenio.modules.deposit.models import Deposition

from invenio.modules.classifier.tasks.classification import (
    classify_paper_with_deposit,
)

from invenio.modules.knowledge.api import get_kb_mappings

from inspire.modules.workflows.tasks.matching import(
    match_record_remote_deposit,
)

from inspire.modules.workflows.tasks.submission import (
    halt_record_with_action,
    send_robotupload_deposit,
    halt_to_render,
    inform_submitter,
    add_files_to_task_results,
)

from inspire.modules.workflows.tasks.actions import (
    was_approved,
    reject_record
)
from invenio.modules.workflows.tasks.logic_tasks import (
    workflow_if,
    workflow_else,
)
from invenio.modules.workflows.tasks.workflows_tasks import log_info
from invenio.modules.workflows.definitions import WorkflowBase

from invenio.base.globals import cfg


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
        add_submission_extra_data,
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(is_dump=False),
        halt_to_render,
        # Get FFT from arXiv, if arXiv ID is provided
        arxiv_fft_get,
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
                send_robotupload_deposit(),
            ],
            workflow_else,
            [
                log_info('Record already in database!'),
                reject_record,
            ],
        ],
        inform_submitter,
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
            return "User submission in progress"

    @staticmethod
    def get_description(bwo):
        """Return description of object."""
        results = bwo.get_tasks_results()
        deposit_object = Deposition(bwo)
        sip = deposit_object.get_latest_sip()
        if sip:
            record = sip.metadata
            identifiers = [record.get("arxiv_id", "")]
            categories = [record.get("type_of_doc", "")]
            return render_template('workflows/styles/submission_record.html',
                                   categories=categories,
                                   identifiers=identifiers,
                                   results=results,
                                   )
        else:
            from invenio.modules.access.control import acc_get_user_email
            id_user = deposit_object.workflow_object.id_user
            return "Submitted by: {0}".format(acc_get_user_email(id_user))

    @staticmethod
    def formatter(bwo, **kwargs):
        """Return formatted data of object."""
        from invenio.modules.formatter import format_record
        deposit_object = Deposition(bwo)
        submission_data = deposit_object.get_latest_sip()
        marcxml = submission_data.package

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
                     'university': "university",
                     'degree_type': "type",
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
                                           'university',
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

        # ============================
        # Abstract, Title and Subjects
        # ============================
        for field in field_list:
            if field in metadata:
                tmp_field = metadata[field]
                metadata[field] = {field_map[field]: tmp_field}

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
                metadata['authors'][0]['full_name'] = ", ".join(first_author)
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
                            k['full_name'] = ", ".join(additional_author)
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
        thesis_fields = filter(lambda field: field in metadata, ['university',
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
        if metadata['type_of_doc'] == 'article':
            metadata['collections'].append({'primary': "Published"})
        elif metadata['type_of_doc'] == 'thesis':
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
        if 'report_number' in metadata and metadata['report_number']:
            user_report_number = metadata['report_number']
            del metadata['report_number']

        # ========
        # arXiv ID
        # ========
        imported_from_arXiv = filter(lambda field: field in metadata,
                                     ['arxiv_id',
                                      'categories_arXiv'])

        if imported_from_arXiv or metadata.get('title_source') == 'arXiv':
            metadata['report_number'] = {'primary': metadata['arxiv_id'],
                                         'source': 'arXiv'}
            if len(metadata['arxiv_id'].split('/')) == 2:
                metadata['report_number']['arxiv_category'] = metadata['arxiv_id'].split('/')[0]
            metadata['abstract']['source'] = 'arXiv'
            if 'categories' in metadata and metadata['categories']:
                # Subject term
                if not isinstance(metadata['categories'], list):
                    metadata['categories'] = [metadata['categories']]
                subject_list = [{"term": c, "scheme": "arXiv"}
                                for c in metadata['categories']]
                if 'subject_term' in metadata and metadata['subject_term']:
                    metadata['subject_term'].extend(subject_list)
                else:
                    metadata['subject_term'] = subject_list
            metadata['system_number_external'] = {'external_key': 'oai:arXiv.org:' + metadata['arxiv_id'],
                                                  'institute': 'arXiv'}
            metadata['collections'].extend([{'primary': "arXiv"}, {'primary': "Citeable"}])

        if user_report_number:
            if 'report_number' in metadata and metadata['report_number']:
                metadata['report_number'] = [metadata['report_number'],
                                             {'primary': user_report_number}]
            else:
                metadata['report_number'] = {'primary': user_report_number}

        # ========
        # Language
        # ========
        if metadata['language'] != 'en':
            metadata['language'] = unicode(dict(LiteratureForm.languages).get(metadata['language']))
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
                fft['flag'] = "HIDDEN"
                del fft['path'], fft['name']

            map(restructure_ffts, metadata['fft'])

        # ====
        # URLs
        # ====
        metadata['url'] = filter(None, metadata['url'])
        if 'url' in metadata and metadata['url']:
            def restructure_urls(url):
                url[''] = url['full_url']
                del url['full_url']

            map(restructure_urls, metadata['url'])

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
                        metadata['page_nr'] = int(pages[1])-int(pages[0])
                    except ValueError:
                        pass

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

            if {'primary': "ConferencePaper"} in metadata['collections']:
                metadata['collections'].remove({'primary': "ConferencePaper"})

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
        sources = ["{0}:{1}".format('inspire:uid:', userid)]
        metadata['acquisition_source'] = dict(
            source=sources,
            email=email,
            method="submission",
            submission_number=deposition.id,
        )

        # ===================
        # Delete useless data
        # ===================
        for key in delete_keys:
            del metadata[key]
