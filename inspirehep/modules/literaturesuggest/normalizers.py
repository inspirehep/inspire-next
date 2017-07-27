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

from sqlalchemy.orm.exc import NoResultFound

from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity

from inspirehep.utils.normalizers import (
    normalize_journal_title as _normalize_journal_title,
)
from inspirehep.utils.pubnote import split_page_artid
from invenio_db import db
from sqlalchemy import text


def check_journal_existance(title):
    query = text("SELECT  id FROM records_metadata as r, json_array_elements_text(r.json -> '_collections') as elem,json_array_elements(r.json-> 'journal_titles') as titles\
    WHERE 'Journals' = elem AND titles->>'title' =:j_title;").bindparams(j_title=title)
    result = db.session.execute(query)
    return result


def check_book_existence(title):
    query = text("SELECT  json FROM records_metadata as r, json_array_elements(r.json -> 'titles') as elem, json_array_elements_text(r.json -> 'document_type') as elem2\
    WHERE elem ->> 'title' =:b_title AND elem2 = 'book'").bindparams(b_title=title)
    result = db.session.execute(query)
    return result


def normalize_formdata(obj, formdata):
    formdata = get_user_orcid(obj, formdata)
    formdata = get_user_email(obj, formdata)
    formdata = split_page_range_article_id(obj, formdata)
    formdata = normalize_journal_title(obj, formdata)
    formdata = remove_english_language(obj, formdata)
    formdata = find_book_id(obj, formdata)

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
        result = check_journal_existance(formdata.get('series_title'))
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
                formdata['parent_book'] = result[0][0]['self']['$ref']
    return formdata


def remove_english_language(obj, formdata):
    if formdata.get('language') == 'en':
        del formdata['language']
        del formdata['title_translation']

    return formdata
