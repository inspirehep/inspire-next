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

from mock import patch

from inspire_schemas.api import LiteratureBuilder, load_schema, validate
from inspirehep.modules.literaturesuggest.utils import formdata_to_model


def test_formdata_to_model_ignores_arxiv_pdf():
    formdata = {
        'type_of_doc': 'article',
        'title': 'Test title',
        'url': 'https://arxiv.org/pdf/1511.04200.pdf'
    }

    _, extra_data = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    expected_extra_data = {}

    assert extra_data == expected_extra_data


def test_formdata_to_model_ignores_arxiv_additional_url():
    formdata = {
        'type_of_doc': 'article',
        'title': 'Test title',
        'additional_url': 'https://arxiv.org/abs/1511.04200'
    }

    data, _ = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    assert 'urls' not in data


def test_formdata_to_model_only_pdf():
    formdata = {
        'type_of_doc': 'article',
        'title': 'Test title',
        'url': 'https://ora.ox.ac.uk/content01.pdf'
    }

    _, extra_data = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    expected_extra_data = {
        'submission_pdf': 'https://ora.ox.ac.uk/content01.pdf'
    }

    assert expected_extra_data == extra_data


def test_formdata_to_model_only_additional_url():
    formdata = {
        'type_of_doc': 'article',
        'title': 'Test title',
        'additional_url': 'https://ora.ox.ac.uk/splash_page.html'
    }

    data, extra_data = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    expected_urls = [{
        'value': 'https://ora.ox.ac.uk/splash_page.html'
    }]

    assert expected_urls == data['urls']
    assert 'submission_pdf' not in extra_data


def test_formdata_to_model_pdf_and_additional_url():
    formdata = {
        'type_of_doc': 'article',
        'title': 'Test title',
        'url': 'https://ora.ox.ac.uk/content01.pdf',
        'additional_url': 'https://ora.ox.ac.uk/splash_page.html'
    }

    data, extra_data = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    expected_extra_data = {
        'submission_pdf': 'https://ora.ox.ac.uk/content01.pdf'
    }

    expected_urls = [{
        'value': 'https://ora.ox.ac.uk/splash_page.html'
    }]

    assert expected_extra_data == extra_data
    assert expected_urls == data['urls']


@patch.object(LiteratureBuilder, 'validate_record')
def test_formdata_to_model_only_book(mock_validate_record):
    schema = load_schema('hep')
    subschema = schema['properties']['book_series']

    formdata = {
        'series_title': 'Astrophysics No2',
        'series_volume': 'Universe',
        'type_of_doc': 'book',
    }

    expected_book_series = [
        {
            'title': 'Astrophysics No2',
            'volume': 'Universe',
        },
    ]
    data, _ = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    assert validate(data['book_series'], subschema) is None
    assert expected_book_series == data['book_series']


@patch.object(LiteratureBuilder, 'validate_record')
def test_formdata_to_model_only_thesis(mock_validate_record):
    schema = load_schema('hep')
    subschema = schema['properties']['thesis_info']

    formdata = {
        'defense_date': '2010-03-03',
        'degree_type': 'phd',
        'institution': 'Harvard',
        'thesis_date': '2011-05-03',
        'type_of_doc': 'thesis',
    }

    expected_thesis_info = {
        'date': '2011-05-03',
        'defense_date': '2010-03-03',
        'degree_type': 'phd',
        'institutions': [
            {'name': 'Harvard'},
        ],
    }
    data, _ = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    assert validate(data['thesis_info'], subschema) is None
    assert expected_thesis_info == data['thesis_info']


@patch.object(LiteratureBuilder, 'validate_record')
def test_formdata_to_model_only_chapter(mock_validate_record):
    schema = load_schema('hep')
    book_series_subschema = schema['properties']['book_series']
    publication_info_subschema = schema['properties']['publication_info']

    formdata = {
        'end_page': '1200',
        'parent_book': 'http://localhost:5000/api/literature/1373790',
        'series_title': 'Astrophysics',
        'start_page': '150',
        'type_of_doc': 'chapter',
    }

    expected_book_series = [
        {'title': 'Astrophysics'},
    ]
    expected_publication_info = [
        {
            'page_end': '1200',
            'page_start': '150',
            'parent_record': {
                '$ref': 'http://localhost:5000/api/literature/1373790',
            },
        },
    ]
    data, _ = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    assert validate(data['book_series'], book_series_subschema) is None
    assert expected_book_series == data['book_series']

    assert validate(data['publication_info'], publication_info_subschema) is None
    assert expected_publication_info == data['publication_info']


@patch.object(LiteratureBuilder, 'validate_record')
def test_formdata_to_model_extra_comments(mock_validate_record):
    schema = load_schema('hep')
    private_notes_subschema = schema['properties']['_private_notes']

    formdata = {'extra_comments': 'Custom user input with comments.'}

    expected_private_notes = [
        {
            'source': 'submitter',
            'value': 'Custom user input with comments.',
        }
    ]
    data, _ = formdata_to_model(formdata=formdata, id_workflow=1, id_user=1)

    validate(data['_private_notes'], private_notes_subschema)
    assert expected_private_notes == data['_private_notes']
