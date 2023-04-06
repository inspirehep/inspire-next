# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import copy
import datetime

from flask import current_app
from idutils import is_arxiv_post_2007
from inspire_schemas.api import LiteratureBuilder
from inspire_schemas.readers import LiteratureReader
from inspire_utils.helpers import force_list
from inspire_utils.record import get_value

from inspirehep.modules.forms.utils import filter_empty_elements
from inspirehep.modules.workflows.utils import with_debug_logging


def formdata_to_model(obj, formdata):
    """Manipulate form data to match literature data model."""
    def _is_arxiv_url(url):
        return 'arxiv.org' in url

    form_fields = copy.deepcopy(formdata)
    filter_empty_elements(
        form_fields, ['authors', 'supervisors', 'report_numbers']
    )

    builder = LiteratureBuilder(source='submitter')

    for author in form_fields.get('authors', []):
        builder.add_author(builder.make_author(
            author['full_name'],
            affiliations=force_list(author['affiliation'])
            if author['affiliation'] else None,
            roles=['author']
        ))

    for supervisor in form_fields.get('supervisors', []):
        builder.add_author(builder.make_author(
            supervisor['full_name'],
            affiliations=force_list(supervisor['affiliation'])
            if author['affiliation'] else None,
            roles=['supervisor']
        ))

    builder.add_title(title=form_fields.get('title'))

    document_type = 'conference paper' if form_fields.get('conf_name') \
        else form_fields.get('type_of_doc', [])
    if document_type == 'chapter':
        document_type = 'book chapter'

    builder.add_document_type(
        document_type=document_type
    )

    builder.add_abstract(
        abstract=form_fields.get('abstract'),
        source='arXiv' if form_fields.get('categories') else None
    )

    if form_fields.get('arxiv_id') and form_fields.get('categories'):
        builder.add_arxiv_eprint(
            arxiv_id=form_fields.get('arxiv_id'),
            arxiv_categories=form_fields.get('categories').split()
        )

    builder.add_doi(doi=form_fields.get('doi'))

    builder.add_inspire_categories(
        subject_terms=form_fields.get('subject_term'),
        source='user'
    )

    for key in ('extra_comments', 'nonpublic_note',
                'hidden_notes', 'conf_name'):
        builder.add_private_note(
            private_notes=form_fields.get(key)
        )

    year = form_fields.get('year')
    try:
        year = int(year)
    except (TypeError, ValueError):
        year = None

    builder.add_preprint_date(
        preprint_date=form_fields.get('preprint_created')
    )

    if form_fields.get('type_of_doc') == 'thesis':
        builder.add_thesis(
            defense_date=form_fields.get('defense_date'),
            degree_type=form_fields.get('degree_type'),
            institution=form_fields.get('institution'),
            date=form_fields.get('thesis_date')
        )

    if form_fields.get('type_of_doc') == 'chapter':
        if not form_fields.get('journal_title'):
            builder.add_book_series(title=form_fields.get('series_title'))

    if form_fields.get('type_of_doc') == 'book':
        if form_fields.get('journal_title'):
            form_fields['volume'] = form_fields.get('series_volume')
        else:
            builder.add_book_series(title=form_fields.get('series_title'),
                                    volume=form_fields.get('series_volume')
                                    )
        builder.add_book(
            publisher=form_fields.get('publisher_name'),
            place=form_fields.get('publication_place'),
            date=form_fields.get('publication_date'))

    builder.add_publication_info(
        year=year,
        cnum=form_fields.get('conference_id'),
        journal_issue=form_fields.get('issue'),
        journal_title=form_fields.get('journal_title'),
        journal_volume=form_fields.get('volume'),
        page_start=form_fields.get('start_page'),
        page_end=form_fields.get('end_page'),
        artid=form_fields.get('artid'),
        parent_record=form_fields.get('parent_book')
    )

    builder.add_accelerator_experiments_legacy_name(
        legacy_name=form_fields.get('experiment')
    )

    language = form_fields.get('other_language') \
        if form_fields.get('language') == 'oth' \
        else form_fields.get('language')
    builder.add_language(language=language)

    if form_fields.get('title_translation'):
        builder.add_title_translation(
            title=form_fields['title_translation'],
            language='en',
        )

    builder.add_title(
        title=form_fields.get('title_arXiv'),
        source='arXiv'
    )

    builder.add_title(
        title=form_fields.get('title_crossref'),
        source='crossref'
    )

    builder.add_license(url=form_fields.get('license_url'))

    builder.add_public_note(public_note=form_fields.get('public_notes'))

    builder.add_public_note(
        public_note=form_fields.get('note'),
        source='arXiv' if form_fields.get('categories') else 'CrossRef'
    )

    form_url = form_fields.get('url')
    form_additional_url = form_fields.get('additional_url')
    if form_url and not _is_arxiv_url(form_url):
        obj.extra_data['submission_pdf'] = form_url
        if not form_additional_url:
            builder.add_url(url=form_url)

    if form_additional_url and not _is_arxiv_url(form_additional_url):
        builder.add_url(url=form_additional_url)

    [builder.add_report_number(
        report_number=report_number.get('report_number')
    ) for report_number in form_fields.get('report_numbers', [])]

    builder.add_collaboration(collaboration=form_fields.get('collaboration'))

    builder.add_acquisition_source(
        datetime=datetime.datetime.utcnow().isoformat(),
        submission_number=obj.id,
        internal_uid=int(obj.id_user),
        email=form_fields.get('email'),
        orcid=form_fields.get('orcid'),
        method='submitter'
    )

    return builder.record


def new_ticket_context(user, obj):
    """Context for literature new tickets."""
    title = LiteratureReader(obj.data).title
    subject = u"Your suggestion to INSPIRE: {0}".format(title)
    user_comment = obj.extra_data.get('formdata', {}).get('extra_comments', '')
    identifiers = get_value(obj.data, "external_system_numbers.value") or []
    return dict(
        email=user.email,
        title=title,
        identifier=identifiers or "",
        user_comment=user_comment,
        references=obj.extra_data.get('formdata', {}).get('references'),
        object=obj,
        subject=subject
    )


def get_user_name(user):
    if hasattr(user, 'given_names'):
        return user.given_names
    else:
        return user.email


def reply_ticket_context(user, obj):
    """Context for literature replies."""
    return dict(
        user_name=get_user_name(user),
        title=LiteratureReader(obj.data).title,
        reason=obj.extra_data.get("reason", ""),
        record_url=obj.extra_data.get("url", ""),
    )


def curation_ticket_context(user, obj):
    recid = obj.extra_data.get('recid')
    record_url = obj.extra_data.get('url')
    server_name = current_app.config['SERVER_NAME']
    legacy_url = current_app.config['LEGACY_BASE_URL']

    arxiv_ids = get_value(obj.data, 'arxiv_eprints.value') or []
    for index, arxiv_id in enumerate(arxiv_ids):
        if arxiv_id and is_arxiv_post_2007(arxiv_id):
            arxiv_ids[index] = 'arXiv:{0}'.format(arxiv_id)

    report_numbers = get_value(obj.data, 'report_numbers.value') or []
    dois = [
        "doi:{0}".format(doi)
        for doi in get_value(obj.data, 'dois.value') or []
    ]
    link_to_pdf = obj.extra_data.get('formdata', {}).get('url')

    subject = ' '.join(filter(
        lambda x: x is not None,
        arxiv_ids + dois + report_numbers + ['(#{0})'.format(recid)]
    ))

    references = obj.extra_data.get('formdata', {}).get('references')
    user_comment = obj.extra_data.get('formdata', {}).get('extra_comments', '')

    return dict(
        email=user.email if user else '',
        link_to_pdf=link_to_pdf,
        recid=recid,
        record_url=record_url,
        references=references,
        server_name=server_name,
        subject=subject,
        user_comment=user_comment,
        legacy_url=legacy_url,
    )


@with_debug_logging
def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    return obj.extra_data.get("core", False)


@with_debug_logging
def check_source_publishing(obj, eng):
    """Check if the a curation ticket is needed."""
    return get_value(obj.data, 'acquisition_source.source').lower() not in {"arxiv", "submitter"}
