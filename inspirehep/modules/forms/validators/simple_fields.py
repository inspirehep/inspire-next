# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015, 2016 CERN.
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

from datetime import datetime
from urllib import urlencode

from flask import current_app
from idutils import is_arxiv, is_isbn
from wtforms.validators import ValidationError, StopValidation


def arxiv_syntax_validation(form, field):
    """Validate ArXiv ID syntax."""
    message = "The provided ArXiv ID is invalid - it should look \
                similar to 'hep-th/9711200' or '1207.7235'."

    if field.data and not is_arxiv(field.data):
        raise StopValidation(message)


def isbn_syntax_validation(form, field):
    """Validate ISBN syntax."""
    message = "The provided ISBN is invalid - it should look \
                similar to '1413304540', '1-4133-0454-0', '978-1413304541' or \
                '978-1-4133-0454-1'."

    if field.data and not is_isbn(field.data):
        raise StopValidation(message)


def does_exist_in_inspirehep(query, collection=None):
    """Check if there exist an item in the db which satisfies query.

    :param query: http query to check
    :param collection: collection to search in; by default searches in
        the default collection
    """
    import requests
    from json import loads

    params = {'p': query, 'of': 'id'}

    if collection:
        params['cc'] = collection

    json_reply = requests.get("http://inspirehep.net/search?", params=params).text

    reply = loads(json_reply)
    # not an array -> invalid answer
    if not isinstance(reply, list):
        raise ValueError('Invalid server answer.')

    # non-empty answer -> duplicate
    if len(reply):
        return True

    return False


def inspirehep_duplicated_validator(inspire_query, property_name, collection=None):
    """Check if a record with the same doi already exists.

    Needs to be wrapped in a function with proper validator signature.
    """
    if does_exist_in_inspirehep(inspire_query, collection):
        url = "http://inspirehep.net/search?" + urlencode({'p': inspire_query})
        if collection:
            url += '&' + urlencode({'cc': collection})
        raise ValidationError(
            'There exists already an item with the same %s. '
            '<a target="_blank" href="%s">See the record.</a>' % (property_name, url)
        )


def duplicated_orcid_validator(form, field):
    """Check if a record with the same ORCID already exists."""
    orcid = field.data
    # TODO: local check for duplicates
    if not orcid:
        return
    if current_app.config.get('PRODUCTION_MODE'):
        inspirehep_duplicated_validator('035__a:' + orcid, 'ORCID', 'HepNames')


def duplicated_doi_validator(form, field):
    """Check if a record with the same doi already exists."""
    doi = field.data
    # TODO: local check for duplicates
    if not doi:
        return
    if current_app.config.get('PRODUCTION_MODE'):
        inspirehep_duplicated_validator('doi:' + doi, 'DOI')


def duplicated_arxiv_id_validator(form, field):
    """Check if a record with the same arXiv ID already exists."""
    arxiv_id = field.data
    # TODO: local check for duplicates
    if not arxiv_id:
        return
    if current_app.config.get('PRODUCTION_MODE'):
        inspirehep_duplicated_validator('035__a:oai:arXiv.org:' + arxiv_id, 'arXiv ID')


def pdf_validator(form, field):
    """Validate that url points to PDF."""
    import requests

    def get_content_type(url):
        session = requests.Session()
        try:
            response = session.head(url, allow_redirects=True)
        except:
            return
        return response.headers['content-type']

    message = "Please, provide an accessible direct link to a PDF document."

    if field.data and get_content_type(field.data) != 'application/pdf':
        raise StopValidation(message)


def date_validator(form, field):
    message = ("Please, provide a valid date in the format YYYY-MM-DD, YYYY-MM" " or YYYY.")
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
