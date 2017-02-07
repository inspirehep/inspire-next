# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016, 2017 CERN.
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

import os
import pkg_resources
import tempfile

import httpretty
import pytest

from inspirehep.utils.helpers import (
    download_file,
    get_json_for_plots,
    force_force_list,
)


@pytest.fixture
def foo_bar_baz():
    return pkg_resources.resource_string(
        __name__, os.path.join('fixtures', 'foo-bar-baz'))


@pytest.mark.httpretty
def test_download_file(foo_bar_baz):
    httpretty.register_uri(
        httpretty.GET, 'http://example.com/foo-bar-baz', body=foo_bar_baz)

    filename = next(tempfile._get_candidate_names())

    expected = filename
    result = download_file(
        'http://example.com/foo-bar-baz', output_file=filename)

    assert expected == result

    with open(filename, 'rb') as f:
        assert 'foo\nbar\nbaz\n' == f.read()

    os.remove(filename)


@pytest.mark.httpretty
def test_download_file_does_not_create_a_file_if_the_request_fails():
    httpretty.register_uri(
        httpretty.GET, 'http://example.com/500', body='', status=500)

    filename = next(tempfile._get_candidate_names())

    expected = filename
    result = download_file(
        'http://example.com/500', output_file=filename)

    assert expected == result

    with pytest.raises(IOError):
        open(filename, 'rb')


@pytest.mark.httpretty
def test_download_file_raises_if_called_without_output_file():
    httpretty.register_uri(
        httpretty.GET, 'http://example.com/foo-bar-baz', body=foo_bar_baz)

    with pytest.raises(IOError):
        download_file('http://example.com/foo-bar-baz')


def test_get_json_for_plots():
    plots = [
        {
            'captions': [
                'foo-caption-1',
                'foo-caption-2',
            ],
            'name': 'foo-name',
            'url': 'http://example.com/foo-url',
        },
        {
            'captions': [
                'bar-caption-1',
            ],
            'name': 'bar-name',
            'url': 'http://example.com/bar-url',
        },
        {
        },
    ]

    expected = {
        '_fft': [
            {
                'path': 'http://example.com/foo-url',
                'type': 'Plot',
                'description': '00000 foo-caption-1foo-caption-2',
                'filename': 'foo-name',
            },
            {
                'path': 'http://example.com/bar-url',
                'type': 'Plot',
                'description': '00001 bar-caption-1',
                'filename': 'bar-name',
            },
            {
                'path': None,
                'type': 'Plot',
                'description': '00002 ',
                'filename': None,
            },
        ],
    }
    result = get_json_for_plots(plots)

    assert expected == result


def test_force_force_list_returns_empty_list_on_none():
    expected = []
    result = force_force_list(None)

    assert expected == result


def test_force_force_list_wraps_strings_in_a_list():
    expected = ['foo']
    result = force_force_list('foo')

    assert expected == result


def test_force_force_list_converts_tuples_to_lists():
    expected = ['foo', 'bar', 'baz']
    result = force_force_list(('foo', 'bar', 'baz'))

    assert expected == result


def test_force_force_list_does_not_touch_lists():
    expected = ['foo', 'bar', 'baz']
    result = force_force_list(['foo', 'bar', 'baz'])

    assert expected == result
