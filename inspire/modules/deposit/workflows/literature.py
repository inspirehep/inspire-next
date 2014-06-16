#
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


from lxml.html import fromstring

from invenio.modules.deposit.types import SimpleRecordDeposition
from invenio.modules.deposit.tasks import render_form, \
    create_recid, \
    prepare_sip, \
    finalize_record_sip, \
    upload_record_sip, \
    prefill_draft, \
    process_sip_metadata, \
    hold_for_approval

from inspire.modules.deposit.forms import LiteratureForm


class literature(SimpleRecordDeposition):

    """Literature deposit submission."""

    workflow = [
        # Pre-fill draft with values passed in from request
        prefill_draft(draft_id='default'),
        # Render form and wait for user to submit
        render_form(draft_id='default'),
        # Create the submission information package by merging form data
        # from all drafts (in this case only one draft exists).
        prepare_sip(),
        # Fills sip with existing ArXiv source
        #harvest_arxiv(),
        # Process metadata to match your JSONAlchemy record model. This will
        # call process_sip_metadata() on your subclass.
        process_sip_metadata(),
        # Reserve a new record id, so that we can provide proper feedback to
        # user before the record has been uploaded.
        create_recid(),
        # Generate MARC based on metadata dictionary.
        finalize_record_sip(is_dump=False),
        # Hold the deposition for admin approval
        hold_for_approval(),
        # Seal the SIP and write MARCXML file and call bibupload on it
        upload_record_sip(),
    ]

    hold_for_upload = False

    name = "Literature"
    name_plural = "Literature depositions"
    group = "Articles & Preprints"
    draft_definitions = {
        'default': LiteratureForm,
    }

    @classmethod
    def process_sip_metadata(cls, deposition, metadata):
        """Map fields to match jsonalchemy configuration."""
        # ========
        # Abstract
        # ========
        if 'abstract' in metadata:
            abstract = metadata['abstract']
            metadata['abstract'] = {}
            metadata['abstract']['abstract'] = abstract

        # =======
        # Title
        # =======
        title = metadata['title']
        metadata['title'] = {}
        metadata['title']['main'] = title

        # =======
        # Subjects
        # =======
        if "subject_term" in metadata:
            subject_term = metadata['subject_term']
            metadata['subject_term'] = {}
            metadata['subject_term']['term'] = subject_term

        # =======
        # Authors
        # =======
        if 'authors' in metadata and metadata['authors']:
            metadata['_first_author'] = metadata['authors'][0]
            metadata['_first_author']['email'] = ''
            if metadata['authors'][1:]:
                metadata['_additional_authors'] = metadata['authors'][1:]
                for k in metadata['_additional_authors']:
                    k['email'] = ''
            del metadata['authors']

        # ===========
        # Supervisors
        # ===========
        if 'supervisors' in metadata and metadata['supervisors']:
            metadata['thesis_supervisor'] = metadata['supervisors'][0]
            metadata['thesis_supervisor']['email'] = ''
            #metadata['_additional_authors'] = metadata['authors'][1:]

        # ==============
        # Thesis related
        # ==============
        if metadata['type_of_doc'] == 'thesis':
            metadata['thesis'] = {}
            if 'defense_date' in metadata:
                metadata['thesis']['date'] = metadata['defense_date']
            if 'university' in metadata:
                metadata['thesis']['university'] = metadata['university']
            if 'degree_type' in metadata:
                metadata['thesis']['type'] = metadata['degree_type']

        # ========
        # Category
        # ========
        metadata['collections'] = {}
        metadata['collections']['primary'] = ['HEP']

        # ==========
        # Experiment
        # ==========
        if 'experiment' in metadata:
            metadata['accelerator_experiment'] = {}
            metadata['accelerator_experiment']['experiment'] = metadata['experiment']

        # ===============
        # Conference Info
        # ===============
        if 'conf_name' in metadata:
            metadata['nonpublic_note'] = metadata['conf_name']
            metadata['collections']['primary'] += ['ConferencePaper']

        # ================
        # Publication Info
        # ================
        metadata['publication_info'] = {}
        if 'journal_title' in metadata:
            metadata['publication_info']['title'] = metadata['journal_title']
        # this should only allow the user to fill whether the page_range or the article_id
        if 'page_range' in metadata:
            metadata['publication_info']['page_artid'] = metadata['page_range']
        elif 'article_id' in metadata:
            metadata['publication_info']['page_artid'] = metadata['article_id']
        if 'volume' in metadata:
            metadata['publication_info']['journal_volume'] = metadata['volume']
        if 'year' in metadata:
            metadata['publication_info']['year'] = metadata['year']
        if 'issue' in metadata:
            metadata['publication_info']['journal_issue'] = metadata['issue']

        # Delete useless data
        delete_keys = ['supervisors',
                       'defense_date',
                       'degree_type',
                       'university',
                       'journal_title',
                       'page_range',
                       'article_id',
                       'volume',
                       'year',
                       'issue',
                       'conf_name',
                       'experiment']
        for key in delete_keys:
            if key in metadata:
                del metadata[key]
