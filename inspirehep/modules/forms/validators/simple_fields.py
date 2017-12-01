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
from flask import current_app, url_for
from flask_login import current_user
from idutils import is_arxiv
from invenio_search import current_search_client as es
from wtforms.validators import ValidationError, StopValidation

from inspire_matcher.api import match
from inspire_schemas.utils import load_schema
from inspire_utils.dedupers import dedupe_list
from inspire_utils.record import get_value

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


def duplicated_validator(property_name, property_value):
    def _is_not_deleted(base_record, match_result):
        return not get_value(match_result, '_source.deleted', default=False)

    config = {
        'algorithm': [
            {
                'queries': [
                    {
                        'path': 'arxiv_id',
                        'search_path': 'arxiv_eprints.value.raw',
                        'type': 'exact',
                    },
                    {
                        'path': 'doi',
                        'search_path': 'dois.value.raw',
                        'type': 'exact',
                    },
                ],
                'validator': _is_not_deleted,
            },
        ],
        'doc_type': 'hep',
        'index': 'records-hep',
    }

    if property_name == 'arXiv ID':
        data = {
            'arxiv_id': property_value,
        }
    if property_name == 'DOI':
        data = {
            'doi': property_value,
        }

    matches = dedupe_list(match(data, config))
    matched_ids = [int(el['_source']['control_number']) for el in matches]
    if matched_ids:
        url = url_for(
            'invenio_records_ui.literature',
            pid_value=matched_ids[0],
        )
        raise ValidationError(
            'There exists already an item with the same %s. '
            '<a target="_blank" href="%s">See the record.</a>'
            % (property_name, url)
        )


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
    doi_property_name = 'DOI'
    doi = field.data
    if not doi:
        return

    # local check for duplicates
    duplicated_validator(
        property_name=doi_property_name,
        property_value=doi,
    )

    if current_app.config.get('PRODUCTION_MODE'):
        user_roles = _get_current_user_roles()

        # First check in default collection
        inspirehep_duplicated_validator('doi:' + doi, doi_property_name)

        # And in Hal, CDS collection
        try:
            inspirehep_duplicated_validator(
                'doi:' + doi,
                doi_property_name,
                collections=['HAL Hidden', 'CDS Hidden'],
            )
        except ValidationError:
            if 'cataloger' in user_roles:
                raise


def duplicated_arxiv_id_validator(form, field):
    """Check if a record with the same arXiv ID already exists."""
    arxiv_property_name = 'arXiv ID'
    arxiv_id = field.data
    if not arxiv_id:
        return

    # local check for duplicates
    duplicated_validator(
        property_name=arxiv_property_name,
        property_value=arxiv_id,
    )

    if current_app.config.get('PRODUCTION_MODE'):
        user_roles = _get_current_user_roles()

        # First check in default collection
        inspirehep_duplicated_validator(
            '035__a:oai:arXiv.org:' + arxiv_id, arxiv_property_name)

        # And in Hal, CDS collection
        try:
            inspirehep_duplicated_validator(
                '035__a:oai:arXiv.org:' + arxiv_id, arxiv_property_name,
                collections=['HAL Hidden', 'CDS Hidden'])
        except ValidationError:
            if 'cataloger' in user_roles:
                raise


def already_pending_in_holdingpen_validator(property_name, value):
    """Check if there's a submission in the holdingpen with the same arXiv ID.
    """
    if property_name == 'arXiv ID':
        query_should = {
            'metadata.arxiv_eprints.value.raw': value,
        }
    elif property_name == 'DOI':
        query_should = {
            'metadata.dois.value.raw': value,
        }

    query = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "term": {
                            "metadata.acquisition_source.source": "submitter"
                        },
                    },
                    {
                        "bool": {
                            "must_not": {
                                "term": {
                                    "_workflow.status": "COMPLETED"
                                }
                            }
                        }
                    }
                ],
                "must": [
                    {
                        "term": query_should,
                    }
                ]
            }
        },
        "_source": {
            "includes": [
                "_id"
            ]
        }
    }

    hits = es.search(
        index='holdingpen-hep',
        doc_type='hep',
        body=query,
    )['hits']['hits']

    matches = dedupe_list(hits)
    holdingpen_ids = [int(el['_id']) for el in matches]

    if holdingpen_ids:
        raise ValidationError(
            'There exists already a pending suggestion with the same %s '
            '"%s", it will be attended to shortly.'
            % (property_name, value)
        )


def doi_already_pending_in_holdingpen_validator(form, field):
    """Check if there's a submission in the holdingpen with the same DOI.
    """
    doi = field.data
    if not doi:
        return

    already_pending_in_holdingpen_validator(
        property_name='DOI',
        value=doi,
    )


def arxiv_id_already_pending_in_holdingpen_validator(form, field):
    """Check if there's a submission in the holdingpen with the same arXiv ID.
    """
    arxiv_id = field.data
    if not arxiv_id:
        return

    already_pending_in_holdingpen_validator(
        property_name='arXiv ID',
        value=arxiv_id,
    )


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


def year_validator(form, field):
    """Validate that the field contains an year in an acceptable range."""
    hep = load_schema('hep')
    min_year = get_value(hep, 'properties.publication_info.items.properties.year.minimum')
    max_year = get_value(hep, 'properties.publication_info.items.properties.year.maximum')

    message = 'Please, provide an year between {} and {}.'.format(min_year, max_year)

    if field.data and not min_year <= int(field.data) <= max_year:
        raise StopValidation(message)
