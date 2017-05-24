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

from datetime import datetime
from json import loads
from urllib import urlencode

import requests
from flask import current_app
from flask.ext.login import current_user
from wtforms.validators import ValidationError, StopValidation

from idutils import is_arxiv

from inspirehep.utils.url import is_pdf_link


def _get_current_user_roles():
    return [r.name for r in current_user.roles]


def arxiv_syntax_validation(form, field):
    """Validate ArXiv ID syntax."""
    message = "The provided ArXiv ID is invalid - it should look \
                similar to 'hep-th/9711200' or '1207.7235'."

    if field.data and not is_arxiv(field.data):
        raise StopValidation(message)


def does_exist_in_inspirehep(query, collections=None):
    """Check if there exist an item in the db which satisfies query.

    :param query: http query to check
    :param collections: collections to search in; by default searches in
        the default collection
    """
    params = {
        'p': query,
        'of': 'id'
    }

    if collections:
        if len(collections) == 1:
            params['cc'] = collections[0]
        else:
            params['c'] = collections

    json_reply = requests.get(
        "http://inspirehep.net/search?", params=params).text

    reply = loads(json_reply)
    # not an array -> invalid answer
    if not isinstance(reply, list):
        raise ValueError('Invalid server answer.')

    # non-empty answer -> duplicate
    if len(reply):
        return True

    return False


def inspirehep_duplicated_validator(inspire_query, property_name, collections=None):
    """Check if a record with the same doi already exists.

    Needs to be wrapped in a function with proper validator signature.
    """
    if does_exist_in_inspirehep(inspire_query, collections):
        url = "http://inspirehep.net/search?" + urlencode({'p': inspire_query})
        if collections:
            if len(collections) == 1:
                url += '&' + urlencode({'cc': collections[0]})
            else:
                for collection in collections:
                    url += '&' + urlencode({'c': collection})

        raise ValidationError(
            'There exists already an item with the same %s. '
            '<a target="_blank" href="%s">See the record.</a>'
            % (property_name, url)
        )


def duplicated_orcid_validator(form, field):
    """Check if a record with the same ORCID already exists."""
    orcid = field.data
    # TODO: local check for duplicates
    if not orcid:
        return
    if current_app.config.get('PRODUCTION_MODE'):
        inspirehep_duplicated_validator('035__a:' + orcid, 'ORCID', collections=['HepNames'])


def duplicated_doi_validator(form, field):
    """Check if a record with the same doi already exists."""
    doi = field.data
    # TODO: local check for duplicates
    if not doi:
        return
    if current_app.config.get('PRODUCTION_MODE'):
        user_roles = _get_current_user_roles()

        # First check in default collection
        inspirehep_duplicated_validator('doi:' + doi, 'DOI')

        # And in Hal, CDS collection
        try:
            inspirehep_duplicated_validator('doi:' + doi, 'DOI', collections=['HAL Hidden', 'CDS Hidden'])
        except ValidationError:
            if 'cataloger' in user_roles:
                raise


def duplicated_arxiv_id_validator(form, field):
    """Check if a record with the same arXiv ID already exists."""
    arxiv_id = field.data
    # TODO: local check for duplicates
    if not arxiv_id:
        return
    if current_app.config.get('PRODUCTION_MODE'):
        user_roles = _get_current_user_roles()

        # First check in default collection
        inspirehep_duplicated_validator(
            '035__a:oai:arXiv.org:' + arxiv_id, 'arXiv ID')

        # And in Hal, CDS collection
        try:
            inspirehep_duplicated_validator(
                '035__a:oai:arXiv.org:' + arxiv_id, 'arXiv ID',
                collections=['HAL Hidden', 'CDS Hidden'])
        except ValidationError:
            if 'cataloger' in user_roles:
                raise


def pdf_validator(form, field):
    """Validate that the field contains a link to a PDF."""
    message = 'Please, provide an accessible direct link to a PDF document.'

    if field.data and not is_pdf_link(field.data):
        raise StopValidation(message)


def no_pdf_validator(form, field):
    """Validate that the field does not contain a link to a PDF."""
    message = 'Please, use the field above to link to a PDF.'

    if field.data and is_pdf_link(field.data):
        raise StopValidation(message)


def date_validator(form, field):
    message = ("Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM"
               " or YYYY.")
    if field.data:
        for date_format in ["%Y-%m-%d", "%Y-%m", "%Y"]:
            try:
                datetime.strptime(field.data, date_format).date()
            except ValueError:
                pass
            else:
                break
        else:
            raise StopValidation(message)
