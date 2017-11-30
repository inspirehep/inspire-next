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

import json

from sqlalchemy import text
from sqlalchemy.orm.exc import NoResultFound

from idutils import normalize_doi
from invenio_accounts.models import User
from invenio_db import db
from invenio_oauthclient.models import UserIdentity

from inspire_schemas.utils import split_page_artid
from inspirehep.utils.normalizers import (
    normalize_journal_title as _normalize_journal_title,
)


def check_book_existence(title):
    query = text("""
        SELECT r.json -> 'self' ->> '$ref' AS self_jsonref
        FROM
            records_metadata AS r
        WHERE
            (r.json -> '_collections') ? 'Literature'
        AND
            (r.json -> 'document_type') ? 'book'
        AND
            (r.json -> 'titles') @> :title
    """).bindparams(title=json.dumps([{
        "title": title
    }]))

    return db.session.execute(query)


def check_journal_existence(title):
    query = text("""
        SELECT r.id
        FROM
            records_metadata AS r
        WHERE
            (r.json -> '_collections') ? 'Journals'
        AND
            (r.json -> 'journal_title' @> :title)
    """).bindparams(title=json.dumps(
        {
            "title": title
        }
    ))

    return db.session.execute(query)


def normalize_formdata(obj, formdata):
    formdata = normalize_provided_doi(obj, formdata)
    formdata = get_user_orcid(obj, formdata)
    formdata = get_user_email(obj, formdata)
    formdata = split_page_range_article_id(obj, formdata)
    formdata = normalize_journal_title(obj, formdata)
    formdata = remove_english_language(obj, formdata)
    formdata = find_book_id(obj, formdata)

    return formdata


def normalize_provided_doi(obj, formdata):
    try:
        doi = formdata.get('doi')
        formdata['doi'] = normalize_doi(doi)
    except AttributeError:
        formdata['doi'] = None

    return formdata


def get_user_email(obj, formdata):
    try:
        formdata['email'] = User.query.get(obj.id_user).email
    except AttributeError:
        formdata['email'] = None

    return formdata


def get_user_orcid(obj, formdata):
    try:
        formdata['orcid'] = UserIdentity.query.filter_by(
            id_user=obj.id_user, method='orcid').one().id
    except NoResultFound:
        formdata['orcid'] = None

    return formdata


def split_page_range_article_id(obj, formdata):
    page_range_article_id = formdata.get('page_range_article_id')

    if page_range_article_id:
        page_start, page_end, artid = split_page_artid(page_range_article_id)
        formdata['start_page'] = page_start
        formdata['end_page'] = page_end
        formdata['artid'] = artid

    return formdata


def normalize_journal_title(obj, formdata):
    if formdata.get('type_of_doc') == 'book' or formdata.get('type_of_doc') == 'chapter':
        result = check_journal_existence(formdata.get('series_title'))
        if result.rowcount > 0:
            formdata['journal_title'] = _normalize_journal_title(formdata.get('series_title'))
    else:
        formdata['journal_title'] = _normalize_journal_title(formdata['journal_title'])
    return formdata


def find_book_id(obj, formdata):
    if formdata.get('type_of_doc') == 'chapter':
        if not formdata.get('parent_book'):
            result = list(check_book_existence(formdata.get('book_title')))
            if len(result) == 1:
                formdata['parent_book'] = result[0][0]
    return formdata


def remove_english_language(obj, formdata):
    if formdata.get('language') == 'en':
        del formdata['language']
        del formdata['title_translation']

    return formdata
