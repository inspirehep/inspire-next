# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import copy

from datetime import date

from flask import current_app

from sqlalchemy.orm.exc import NoResultFound

from idutils import is_arxiv_post_2007
from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity
from inspirehep.modules.forms.utils import filter_empty_elements
from inspirehep.modules.search.api import JournalsSearch
from inspirehep.utils.record import get_title, get_value

from .dojson.model import literature


def formdata_to_model(obj, formdata):
    """Manipulate form data to match literature data model."""
    form_fields = copy.deepcopy(formdata)
    filter_empty_elements(
        form_fields, ['authors', 'supervisors', 'report_numbers']
    )

    data = literature.do(form_fields)

    # Add extra fields that need to be computed or depend on other
    # fields.
    #
    # ======
    # Schema
    # ======
    if '$schema' in data and not data['$schema'].startswith('http'):
        jsonschemas_ext = current_app.extensions.get('invenio-jsonschemas')
        data['$schema'] = jsonschemas_ext.path_to_url(
            "records/{0}".format(data['$schema']))

    # ============================
    # Collection
    # ============================
    data['collections'] = [{'primary': "HEP"}]
    if form_fields['type_of_doc'] == 'thesis':
        data['collections'].append({'primary': "THESIS"})

    if get_value(form_fields, "arxiv_eprints.categories", None):
        # Check if it was imported from arXiv
        data['collections'].extend([{'primary': "arXiv"},
                                    {'primary': "Citeable"}])
        # Add arXiv as source
        if data.get("abstracts"):
            data['abstracts'][0]['source'] = 'arXiv'
        if form_fields.get("arxiv_id"):
            data['external_system_numbers'] = [{
                'value': 'oai:arXiv.org:' + form_fields['arxiv_id'],
                'institute': 'arXiv'
            }]
    if "publication_info" in data:
        pub_keys = data['publication_info'][0].keys()

        has_pub_info = all([
            key in pub_keys for key in (
                'year', 'journal_issue', 'journal_volume')])
        has_page_or_artid = any([
            key in pub_keys for key in ('page_start', 'page_end', 'artid')])

        if has_pub_info and has_page_or_artid:
            # NOTE: Only peer reviewed journals should have this collection
            # we are adding it here but ideally should be manually added
            # by a curator.
            data['collections'].append({'primary': "Published"})
            # Add Citeable collection if not present
            collections = [x['primary'] for x in data['collections']]
            if "Citeable" not in collections:
                data['collections'].append({'primary': "Citeable"})
    # ============================
    # Title source and cleanup
    # ============================
    try:
        # Clean up all extra spaces in title
        data['titles'][0]['title'] = " ".join(
            data['titles'][0]['title'].split()
        )
        title = data['titles'][0]['title']
    except (KeyError, IndexError):
        title = ""
    if form_fields.get('title_arXiv'):
        title_arxiv = " ".join(form_fields.get('title_arXiv').split())
        if title == title_arxiv:
            data['titles'][0]["source"] = "arXiv"
        else:
            data['titles'].append({
                'title': title_arxiv,
                'source': "arXiv"
            })
    if form_fields.get('title_crossref'):
        title_crossref = " ".join(
            form_fields.get('title_crossref').split()
        )
        if title == title_crossref:
            data['titles'][0]["source"] = "CrossRef"
        else:
            data['titles'].append({
                'title': title_crossref,
                'source': "CrossRef"
            })
    try:
        data['titles'][0]['source']
    except KeyError:
        # Title has no source, so should be the submitter
        data['titles'][0]['source'] = "submitter"

    # ============================
    # Conference name
    # ============================
    if 'conf_name' in form_fields:
        if 'nonpublic_note' in form_fields:
            data.setdefault("hidden_notes", []).append({
                "value": form_fields['conf_name']
            })
            data['hidden_notes'].append({
                'value': form_fields['nonpublic_note']
            })
        else:
            data.setdefault("hidden_notes", []).append({
                "value": form_fields['conf_name']
            })
        data['collections'].extend([{'primary': "ConferencePaper"}])

    # ============================
    # Page number
    # ============================
    if 'number_of_pages' not in data:
        first_publication_info = data.get('publication_info', [{}])[0]

        page_start = first_publication_info.get('page_start')
        page_end = first_publication_info.get('page_end')

        if page_start and page_end:
            try:
                data['number_of_pages'] = int(page_end) - int(page_start) + 1
            except (TypeError, ValueError):
                pass

    # ============================
    # Language
    # ============================
    if form_fields.get('language') == 'oth':
        if form_fields.get("other_language"):
            data["languages"] = [form_fields["other_language"]]

    # ==========
    # Owner Info
    # ==========
    # TODO Make sure we are getting the email correctly
    userid = obj.id_user
    try:
        email = User.query.get(userid).email
    except AttributeError:
        email = ''
    try:
        # TODO Make sure we are getting the ORCID id correctly
        source = UserIdentity.query.filter_by(id_user=userid, method='orcid').one()
    except NoResultFound:
        source = ''
    if source:
        source = source.method + ':' + source.id
    data['acquisition_source'] = dict(
        source=source,
        email=email,
        date=date.today().isoformat(),
        method="submission",
        submission_number=str(obj.id),
    )
    # ==============
    # Extra comments
    # ==============
    if form_fields.get('extra_comments'):
        data.setdefault('hidden_notes', []).append(
            {
                'value': form_fields['extra_comments'],
                'source': 'submitter'
            }
        )
    # ==========================
    # Journal name normalization
    # ==========================
    journal_title = get_value(data, 'publication_info[0].journal_title')
    if journal_title:
        hits = JournalsSearch().query(
            'match', title_variants__title__lowercased=journal_title).execute()

        if hits:
            try:
                short_title = hits[0].short_titles[0].title
                data['publication_info'][0]['journal_title'] = short_title
            except (AttributeError, IndexError):
                pass

    # Finally, return the converted data
    return data


def new_ticket_context(user, obj):
    """Context for literature new tickets."""
    title = get_title(obj.data)
    subject = "Your suggestion to INSPIRE: {0}".format(title)
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


def reply_ticket_context(user, obj):
    """Context for literature replies."""
    return dict(
        object=obj,
        user=user,
        title=get_title(obj.data),
        reason=obj.extra_data.get("reason", ""),
        record_url=obj.extra_data.get("url", ""),
    )


def curation_ticket_context(user, obj):
    recid = obj.extra_data.get('recid')
    record_url = obj.extra_data.get('url')

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

    references = obj.extra_data.get('formdata').get('references')
    user_comment = obj.extra_data.get('formdata', {}).get('extra_comments', '')

    return dict(
        recid=recid,
        record_url=record_url,
        link_to_pdf=link_to_pdf,
        email=user.email,
        references=references,
        user_comment=user_comment,
        subject=subject
    )


def curation_ticket_needed(obj, eng):
    """Check if the a curation ticket is needed."""
    return obj.extra_data.get("core", False)
