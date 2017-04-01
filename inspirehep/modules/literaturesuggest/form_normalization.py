# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

from inspirehep.utils.pubnote import split_page_artid
from inspirehep.utils.normalizers import normalize_journal_title


def normalization_formdata(workflow_object, formdata):
    formdata = get_user_orcid(workflow_object, formdata)
    formdata = get_user_mail(workflow_object, formdata)
    formdata = split_page_artid_normalization(formdata)
    formdata = journal_title_normalization(formdata)
    formdata = remove_english_language(formdata)

    return formdata


def split_page_artid_normalization(data):
    page_range = data.get('page_range_article_id')

    if page_range:
        data['page_start'], data['page_end'], data['artid'] = split_page_artid(page_range)

    return data


def journal_title_normalization(data):
    if data.get('journal_title'):
        data['journal_title'] = normalize_journal_title(
            data['journal_title']
        )
    return data


def get_user_mail(workflow_obj, data):
    try:
        data['email'] = User.query.get(workflow_obj.id_user).email
    except AttributeError:
        data['email'] = None

    return data


def get_user_orcid(workflow_obj, data):
    try:
        data['orcid'] = UserIdentity.query.filter_by(
            id_user=workflow_obj.id_user,
            method='orcid'
        ).one().id
    except NoResultFound:
        data['orcid'] = None

    return data


def remove_english_language(data):
    if data.get('language') == 'en':
        del data['language']

    return data
