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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from inspirehep.utils.bibtex import Bibtex

from invenio_oauthclient.models import RemoteAccount, UserIdentity

from .schema import orcid_overdo


def convert_to_orcid(record):
    """ Converts a given record to a json containing the information that
    orcid needs.
    """
    orcid_json = orcid_overdo.do(record)

    orcid_json['external-identifiers'] = {
        'work-external-identifier': orcid_json['work_external_identifier']}
    orcid_json.pop('work_external_identifier')
    orcid_json['citation'] = {'citation': Bibtex(
        record).format(), 'citation-type': 'BIBTEX'}

    return orcid_json


def get_authors_credentials(author):
    """Returns the orcid-id and the orcid-token for a specific author (if available)."""
    author_orcid = ''
    for orcid_id in author['ids']:
        if orcid_id['type'] == 'ORCID':
            author_orcid = orcid_id['value']
    raw_user = UserIdentity.query.filter_by(
        id=author_orcid, method='orcid').first()
    user = RemoteAccount.query.filter_by(user_id=raw_user.id_user).first()
    token = user.tokens[0].access_token
    return (token, author_orcid)
