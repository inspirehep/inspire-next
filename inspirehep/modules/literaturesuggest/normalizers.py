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


def normalize_formdata(obj, formdata):
    formdata = get_user_orcid(obj, formdata)
    formdata = get_user_email(obj, formdata)
    formdata = split_page_range_article_id(obj, formdata)
    formdata = normalize_journal_title(obj, formdata)

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
        formdata['page_start'] = page_start
        formdata['page_end'] = page_end
        formdata['artid'] = artid

    return formdata


def normalize_journal_title(obj, formdata):
    if formdata.get('journal_title'):
        formdata['journal_title'] = _normalize_journal_title(formdata['journal_title'])

    return formdata
