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

import pytest
import requests_mock
from mock import patch
from wtforms.validators import StopValidation, ValidationError

from inspirehep.modules.forms.validators.simple_fields import (
    already_pending_in_holdingpen_validator,
    arxiv_syntax_validation,
    date_validator,
    duplicated_validator,
    duplicated_doi_validator,
    duplicated_arxiv_id_validator,
    no_pdf_validator,
    pdf_validator,
    year_validator,
)


class MockField(object):
    def __init__(self, data):
        self.data = data


def test_arxiv_syntax_validation_accepts_valid_new_arxiv_identifiers():
    field = MockField(u'1207.7235')

    assert arxiv_syntax_validation(None, field) is None


def test_arxiv_syntax_validation_accepts_valid_new_arxiv_identifiers_with_arxiv_prefix():
    field = MockField(u'arXiv:1001.4538')

    assert arxiv_syntax_validation(None, field) is None


def test_arxiv_syntax_validation_raises_on_invalid_new_arxiv_identifiers():
    field = MockField(u'1207/7235')

    with pytest.raises(StopValidation):
        arxiv_syntax_validation(None, field)


def test_arxiv_syntax_validation_accepts_valid_old_arxiv_identifiers():
    field = MockField(u'hep-th/9711200')

    assert arxiv_syntax_validation(None, field) is None


def test_arxiv_syntax_validation_raises_on_invalid_old_arxiv_identifiers():
    field = MockField(u'hep-th.9711200')

    with pytest.raises(StopValidation):
        arxiv_syntax_validation(None, field)


def test_date_validator_accepts_valid_dates():
    field = MockField(u'2016')

    assert date_validator(None, field) is None

    field = MockField(u'2016-01')

    assert date_validator(None, field) is None

    field = MockField(u'2016-01-01')

    assert date_validator(None, field) is None


def test_date_validator_accepts_the_empty_string():
    field = MockField(u'')

    assert date_validator(None, field) is None


def test_date_validator_raises_on_invalid_dates():
    field = MockField(u'2016-13')

    with pytest.raises(StopValidation):
        assert date_validator(None, field) is None

    field = MockField(u'2016-02-30')

    with pytest.raises(StopValidation):
        assert date_validator(None, field) is None


def test_pdf_validator_raises_on_link_to_not_a_pdf():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://example.com/not-a-pdf',
            text='<!doctype html>',
            headers={'content-type': 'text/html; charset=utf-8'},
        )

        field = MockField('http://example.com/not-a-pdf')

        with pytest.raises(StopValidation):
            pdf_validator(None, field)


def test_pdf_validator_accepts_a_link_to_a_pdf():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://example.com/a-pdf',
            text='%PDF1.3',
            headers={'content-type': 'application/pdf'},
        )

        field = MockField('http://example.com/a-pdf')

        assert pdf_validator(None, field) is None


def test_pdf_validator_accepts_a_link_to_a_pdf_on_a_misconfigured_server():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://example.com/a-pdf',
            text='%PDF1.3',
            headers={'content-type': 'image/pdf;charset=ISO-8859-1'},
        )

        field = MockField('http://example.com/a-pdf')

        assert pdf_validator(None, field) is None


def test_no_pdf_validator_raises_on_link_to_a_pdf():
    with requests_mock.Mocker() as requests_mocker:
        requests_mocker.register_uri(
            'GET', 'http://example.com/a-pdf',
            text='%PDF1.3',
            headers={'content-type': 'application/pdf'},
        )

        field = MockField('http://example.com/a-pdf')

        with pytest.raises(StopValidation):
            no_pdf_validator(None, field)


def test_year_validator_accepts_a_valid_year():
    field = MockField(u'1993')

    assert year_validator(None, field) is None


def test_year_validator_raises_on_year_invalid_because_too_early():
    field = MockField(u'999')

    with pytest.raises(StopValidation):
        year_validator(None, field)


def test_year_validator_raises_on_year_invalid_because_too_late():
    field = MockField(u'2051')

    with pytest.raises(StopValidation):
        year_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.match')
def test_duplicated_validator_existing_arxiv_invalid(match_mock):
    match_mock.return_value = [{'_source': {'control_number': 123}}]

    with pytest.raises(ValidationError):
        duplicated_validator('arXiv ID', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.match')
def test_duplicated_validator_non_existing_arxiv_valid(match_mock):
    match_mock.return_value = []

    duplicated_validator('arXiv ID', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.match')
def test_duplicated_validator_existing_doi_invalid(match_mock):
    match_mock.return_value = [{'_source': {'control_number': 123}}]

    with pytest.raises(ValidationError):
        duplicated_validator('DOI', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.match')
def test_duplicated_validator_non_existing_doi_valid(match_mock):
    match_mock.return_value = []

    duplicated_validator('DOI', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.match')
def test_duplicated_doi_validator_local_existing_doi_invalid(match_mock):
    match_mock.return_value = [{'_source': {'control_number': 123}}]
    field = MockField(u'10.1088/1475-7516/2013/12/014')

    with pytest.raises(ValidationError):
        duplicated_doi_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.match')
@patch(
    'inspirehep.modules.forms.validators.simple_fields'
    '.does_exist_in_inspirehep'
)
@patch(
    'inspirehep.modules.forms.validators.simple_fields._get_current_user_roles'
)
def test_duplicated_doi_validator_remote_existing_doi_invalid(
    get_current_user_roles_mock,
    does_exist_in_inspirehep_mock,
    match_mock,
):
    match_mock.return_value = []
    does_exist_in_inspirehep_mock.return_value = True
    get_current_user_roles_mock.return_value = ['cataloger']
    field = MockField(u'10.1088/1475-7516/2013/12/014')

    with pytest.raises(ValidationError):
        duplicated_doi_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.match')
@patch(
    'inspirehep.modules.forms.validators.simple_fields'
    '.does_exist_in_inspirehep'
)
@patch(
    'inspirehep.modules.forms.validators.simple_fields._get_current_user_roles'
)
def test_duplicated_doi_validator_not_exsting_anywhere_valid(
    get_current_user_roles_mock,
    does_exist_in_inspirehep_mock,
    match_mock,
):
    match_mock.return_value = []
    does_exist_in_inspirehep_mock.return_value = False
    get_current_user_roles_mock.return_value = ['cataloger']
    field = MockField(u'10.1088/1475-7516/2013/12/014')

    duplicated_doi_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.match')
def test_duplicated_arxiv_id_validator_local_existing_doi_invalid(match_mock):
    match_mock.return_value = [{'_source': {'control_number': 123}}]
    field = MockField(u'1207.7235')

    with pytest.raises(ValidationError):
        duplicated_arxiv_id_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.match')
@patch(
    'inspirehep.modules.forms.validators.simple_fields'
    '.does_exist_in_inspirehep'
)
@patch(
    'inspirehep.modules.forms.validators.simple_fields._get_current_user_roles'
)
def test_duplicated_arxiv_id_validator_remote_existing_doi_invalid(
    get_current_user_roles_mock,
    does_exist_in_inspirehep_mock,
    match_mock,
):
    match_mock.return_value = []
    does_exist_in_inspirehep_mock.return_value = True
    get_current_user_roles_mock.return_value = ['cataloger']
    field = MockField(u'1207.7235')

    with pytest.raises(ValidationError):
        duplicated_arxiv_id_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.match')
@patch(
    'inspirehep.modules.forms.validators.simple_fields'
    '.does_exist_in_inspirehep'
)
@patch(
    'inspirehep.modules.forms.validators.simple_fields._get_current_user_roles'
)
def test_duplicated_arxiv_id_validator_not_exsting_anywhere_valid(
    get_current_user_roles_mock,
    does_exist_in_inspirehep_mock,
    match_mock,
):
    match_mock.return_value = []
    does_exist_in_inspirehep_mock.return_value = False
    get_current_user_roles_mock.return_value = ['cataloger']
    field = MockField(u'1207.7235')

    duplicated_arxiv_id_validator(None, field)


@patch('inspirehep.modules.forms.validators.simple_fields.es')
def test_already_pending_in_holdingpen_validator_arxiv_id_non_existing_valid(
    es_mock,
):
    es_mock.search.return_value = {
        'hits': {
            'hits': [],
        }
    }

    already_pending_in_holdingpen_validator('arXiv ID', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.es')
def test_already_pending_in_holdingpen_validator_arxiv_id_existing_invalid(
    es_mock,
):
    es_mock.search.return_value = {
        'hits': {
            'hits': [{'_id': '123'}],
        }
    }

    with pytest.raises(ValidationError):
        already_pending_in_holdingpen_validator('arXiv ID', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.es')
def test_already_pending_in_holdingpen_validator_doi_non_existing_valid(
    es_mock,
):
    es_mock.search.return_value = {
        'hits': {
            'hits': [],
        }
    }

    already_pending_in_holdingpen_validator('DOI', 'dummy_id')


@patch('inspirehep.modules.forms.validators.simple_fields.es')
def test_already_pending_in_holdingpen_validator_doi_existing_invalid(
    es_mock,
):
    es_mock.search.return_value = {
        'hits': {
            'hits': [{'_id': '123'}],
        }
    }

    with pytest.raises(ValidationError):
        already_pending_in_holdingpen_validator('DOI', 'dummy_id')
