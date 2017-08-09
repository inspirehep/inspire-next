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

import httpretty
import pytest
from wtforms.validators import StopValidation

from inspirehep.modules.forms.validators.simple_fields import (
    no_pdf_validator,
    pdf_validator,
    year_validator,
)


class MockField(object):
    def __init__(self, data):
        self.data = data


@pytest.mark.httpretty
def test_pdf_validator_raises_on_link_to_not_a_pdf():
    httpretty.register_uri(
        httpretty.GET,
        'http://example.com/not-a-pdf',
        body='<!doctype html>',
        content_type='text/html; charset=utf-8',
    )

    field = MockField('http://example.com/not-a-pdf')

    with pytest.raises(StopValidation):
        pdf_validator(None, field)


@pytest.mark.httpretty
def test_pdf_validator_accepts_a_link_to_a_pdf():
    httpretty.register_uri(
        httpretty.GET,
        'http://example.com/a-pdf',
        body='%PDF1.3',
        content_type='application/pdf',
    )

    field = MockField('http://example.com/a-pdf')

    assert pdf_validator(None, field) is None


@pytest.mark.httpretty
def test_pdf_validator_accepts_a_link_to_a_pdf_on_a_misconfigured_server():
    httpretty.register_uri(
        httpretty.GET,
        'http://example.com/a-pdf',
        body='%PDF1.3',
        content_type='image/pdf;charset=ISO-8859-1',
    )

    field = MockField('http://example.com/a-pdf')

    assert pdf_validator(None, field) is None


@pytest.mark.httpretty
def test_no_pdf_validator_raises_on_link_to_a_pdf():
    httpretty.register_uri(
        httpretty.GET,
        'http://example.com/a-pdf',
        body='%PDF1.3',
        content_type='application/pdf',
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
